from flask import Blueprint, jsonify, Response


swagger_bp = Blueprint("swagger_docs", __name__, url_prefix="/api/docs")

_REGISTRY = []


def swagger_operation(path, method, summary, description, *, request_body=None, responses=None, tags=None, security=None):
    """Attach OpenAPI metadata to a view function."""

    def decorator(func):
        _REGISTRY.append(
            {
                "path": path,
                "method": method.lower(),
                "summary": summary,
                "description": description,
                "request_body": request_body,
                "responses": responses or {},
                "tags": tags or ["Authentication"],
                "security": security,
            }
        )
        return func

    return decorator


def _build_spec():
    paths = {}

    for entry in _REGISTRY:
        operation = {
            "summary": entry["summary"],
            "description": entry["description"],
            "tags": entry["tags"],
            "responses": entry["responses"],
        }

        if entry["request_body"]:
            operation["requestBody"] = entry["request_body"]

        if entry["security"] is not None:
            operation["security"] = entry["security"]

        paths.setdefault(entry["path"], {})[entry["method"]] = operation

    return {
        "openapi": "3.0.3",
        "info": {
            "title": "AgriTech Authentication API",
            "version": "1.0.0",
            "description": "OpenAPI documentation for the AgriTech authentication endpoints.",
        },
        "servers": [
            {
                "url": "http://localhost:5000",
                "description": "Local development server",
            }
        ],
        "tags": [
            {
                "name": "Authentication",
                "description": "User registration, login, session management, and password recovery.",
            }
        ],
        "components": {
            "securitySchemes": {
                "bearerAuth": {
                    "type": "http",
                    "scheme": "bearer",
                    "bearerFormat": "JWT",
                }
            }
        },
        "paths": paths,
    }


@swagger_bp.route("/openapi.json", methods=["GET"])
def openapi_json():
    return jsonify(_build_spec())


@swagger_bp.route("/", methods=["GET"])
def swagger_ui():
    html = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>AgriTech API Docs</title>
  <link rel="stylesheet" href="https://unpkg.com/swagger-ui-dist@5/swagger-ui.css" />
  <style>
    body {
      margin: 0;
      background: #f6f8fb;
      font-family: Arial, sans-serif;
    }
    .swagger-header {
      padding: 16px 24px;
      background: #1f6f3f;
      color: #fff;
    }
    .swagger-header h1 {
      margin: 0;
      font-size: 1.4rem;
    }
    .swagger-header p {
      margin: 6px 0 0;
      opacity: 0.9;
    }
  </style>
</head>
<body>
  <header class="swagger-header">
    <h1>AgriTech Authentication API</h1>
    <p>Local Swagger UI for testing registration, login, password recovery, and session endpoints.</p>
  </header>
  <div id="swagger-ui"></div>
  <script src="https://unpkg.com/swagger-ui-dist@5/swagger-ui-bundle.js"></script>
  <script>
    window.ui = SwaggerUIBundle({
      url: './openapi.json',
      dom_id: '#swagger-ui',
      deepLinking: true,
      displayRequestDuration: true,
      presets: [SwaggerUIBundle.presets.apis],
      layout: 'BaseLayout'
    });
  </script>
</body>
</html>
"""
    return Response(html, mimetype="text/html")
