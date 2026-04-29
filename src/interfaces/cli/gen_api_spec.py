import argparse
import asyncio
from typing import Any


async def fetch_openapi(url: str) -> dict[str, Any]:
    import httpx

    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        response.raise_for_status()
        return response.json()


def resolve_ref(ref: str, openapi: dict[str, Any]) -> dict[str, Any]:
    parts = ref.replace("#/", "").split("/")
    current = openapi
    for part in parts:
        if part in current:
            current = current[part]
        else:
            return {}
    return current


def resolve_type(schema: dict[str, Any], openapi: dict[str, Any]) -> str:
    if "$ref" in schema:
        resolved = resolve_ref(schema["$ref"], openapi)
        name = schema["$ref"].split("/")[-1]
        return resolve_type(resolved, openapi) if resolved and "enum" in resolved else name

    if "allOf" in schema:
        return resolve_type(schema["allOf"][0], openapi)

    if "oneOf" in schema:
        types = [resolve_type(s, openapi) for s in schema["oneOf"]]
        return f"({' | '.join(types)})"

    if "anyOf" in schema:
        types = [resolve_type(s, openapi) for s in schema["anyOf"]]
        return f"({' | '.join(types)})"

    type_map = {
        "string": "string",
        "integer": "number",
        "number": "number",
        "boolean": "boolean",
        "array": "array",
        "object": "object",
    }

    schema_type = schema.get("type")
    if schema_type == "null" or schema_type is None:
        result_type = "null"
    else:
        result_type = type_map.get(schema_type, "null")

    if schema.get("type") == "array" and "items" in schema:
        item_type = resolve_type(schema["items"], openapi)
        result_type = f"{item_type}[]"

    return result_type


def format_ts_field(name: str, schema: dict[str, Any], openapi: dict[str, Any]) -> str:
    is_required = name in schema.get("required", [])
    field_schema = schema.get("properties", {}).get(name, {})
    field_type = resolve_type(field_schema, openapi)

    if field_schema.get("nullable"):
        field_type = f"{field_type} | null"

    if is_required:
        return f"  {name}: {field_type};"
    return f"  {name}?: {field_type};"


def parse_params(details: dict[str, Any], openapi: dict[str, Any]) -> tuple[list[str], list[str]]:
    path_params = []
    query_params = []

    for param in details.get("parameters", []):
        param_name = param.get("name", "")
        param_schema = param.get("schema", {})
        param_type = resolve_type(param_schema, openapi)

        if param.get("in") == "path":
            path_params.append(f"{param_name}: {param_type}")
        elif param.get("in") == "query":
            if param.get("required"):
                query_params.append(f"{param_name}: {param_type}")
            else:
                query_params.append(f"{param_name}?: {param_type} | null")

    return path_params, query_params


def parse_response(details: dict[str, Any], openapi: dict[str, Any]) -> str:
    for status, response in details.get("responses", {}).items():
        if status.startswith("2") or status == "default":
            content = response.get("content", {})
            if "application/json" in content:
                json_schema = content["application/json"].get("schema", {})
                if "$ref" in json_schema:
                    return json_schema["$ref"].split("/")[-1]
                elif "items" in json_schema:
                    if "$ref" in json_schema["items"]:
                        item_name = json_schema["items"]["$ref"].split("/")[-1]
                        return f"{item_name}[]"
                    else:
                        return f"{resolve_type(json_schema['items'], openapi)}[]"
    return "any"


def parse_request_body(details: dict[str, Any], openapi: dict[str, Any]) -> str | None:
    request_body = details.get("requestBody")
    if not request_body:
        return None

    content = request_body.get("content", {})

    if "application/json" in content:
        json_schema = content["application/json"].get("schema", {})
        if "$ref" in json_schema:
            return json_schema["$ref"].split("/")[-1]
        if "items" in json_schema:
            if "$ref" in json_schema["items"]:
                return f"{json_schema['items']['$ref'].split('/')[-1]}[]"
            return f"{resolve_type(json_schema['items'], openapi)}[]"

    for content_type in ("multipart/form-data", "application/x-www-form-urlencoded"):
        if content_type in content:
            schema = content[content_type].get("schema", {})
            if "$ref" in schema:
                ref_name = schema["$ref"].split("/")[-1]
                resolved = resolve_ref(schema["$ref"], openapi)
                if resolved and "properties" in resolved:
                    schema = resolved
            if "properties" in schema:
                fields = []
                required = schema.get("required", [])
                for field_name, field_schema in schema.get("properties", {}).items():
                    field_type = resolve_type(field_schema, openapi)
                    if field_schema.get("nullable"):
                        field_type = f"{field_type} | null"
                    if field_name in required:
                        fields.append(f"{field_name}: {field_type}")
                    else:
                        fields.append(f"{field_name}?: {field_type}")
                return f"FormData {{ {', '.join(fields)} }}"

    return None


def parse_endpoints(openapi: dict[str, Any]) -> list[tuple[str, str, list[str], list[str], str | None, str]]:
    endpoints = []

    for path, methods in openapi.get("paths", {}).items():
        for method, details in methods.items():
            if method not in ("get", "post", "put", "delete", "patch"):
                continue

            path_params, query_params = parse_params(details, openapi)
            body_schema = parse_request_body(details, openapi)
            response_schema = parse_response(details, openapi)

            endpoints.append((method.upper(), path, path_params, query_params, body_schema, response_schema))

    return endpoints


def parse_schemas(openapi: dict[str, Any]) -> dict[str, list[str]]:
    schemas = openapi.get("components", {}).get("schemas", {})

    result = {}
    for name, schema in schemas.items():
        if "enum" in schema:
            continue

        properties = schema.get("properties", {})
        fields = []
        for field_name, field_schema in properties.items():
            formatted = format_ts_field(field_name, schema, openapi)
            fields.append(formatted)

        if fields:
            result[name] = fields

    return result


async def main():
    parser = argparse.ArgumentParser(description="Generate API spec from OpenAPI JSON")
    parser.add_argument("--url", default="http://localhost:8000/openapi.json", help="OpenAPI JSON URL")
    parser.add_argument("--output", default="api_spec.ts", help="Output file path")
    args = parser.parse_args()

    openapi = await fetch_openapi(args.url)

    endpoints = parse_endpoints(openapi)
    schemas = parse_schemas(openapi)

    lines = ["// Endpoints", ""]

    for method, path, path_params, query_params, body, response in sorted(endpoints, key=lambda x: (x[0], x[1])):
        lines.append(f"// {method} {path}")
        if path_params:
            lines.append(f"// Path: {{{', '.join(path_params)}}}")
        if query_params:
            lines.append(f"// Query: {{ {', '.join(query_params)} }}")
        if body:
            lines.append(f"// Body: {body}")
        lines.append(f"// Response: {response}")
        lines.append("")

    lines.append("// Schemas")
    lines.append("")

    for name, fields in sorted(schemas.items()):
        lines.append(f"interface {name} {{")
        for field in fields:
            lines.append(field)
        lines.append("}")
        lines.append("")

    output = "\n".join(lines)

    with open(args.output, "w", encoding="utf-8") as f:
        f.write(output)

    print(f"API spec saved to {args.output}")


if __name__ == "__main__":
    asyncio.run(main())
