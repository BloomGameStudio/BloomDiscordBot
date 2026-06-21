"""
Azure Function App - Discord Interactions HTTP Trigger

This is the entry point for Azure Functions.
Receives HTTP POST requests from Discord and routes them to handlers.

To deploy:
1. Create function_app.py in root of Azure Function project
2. Configure triggers via function_app.py or Azure Portal
"""

import azure.functions as func
import json
import logging
from serverless.router import create_router

app = func.FunctionApp()

# Initialize router on startup
router = create_router()
logger = logging.getLogger(__name__)


@app.route(route="interactions", methods=["POST"])
async def interactions_endpoint(req: func.HttpRequest) -> func.HttpResponse:
    """
    HTTP endpoint for Discord interactions.

    Discord sends POST requests here with:
    - X-Signature-Ed25519: Ed25519 signature
    - X-Signature-Timestamp: Request timestamp
    - Body: JSON interaction payload

    Returns:
        JSON response for Discord
    """
    try:
        # Extract headers
        signature = req.headers.get("X-Signature-Ed25519")
        timestamp = req.headers.get("X-Signature-Timestamp")

        if not signature or not timestamp:
            logger.warning("Missing required headers for Discord signature verification")
            return func.HttpResponse(
                json.dumps({"error": "Missing required headers"}),
                status_code=401,
                mimetype="application/json",
            )

        # Get raw body
        body = req.get_body().decode("utf-8")

        # Validate request signature
        if not router.validate_request(signature, timestamp, body):
            logger.warning("Invalid Discord signature")
            return func.HttpResponse(
                json.dumps({"error": "Invalid signature"}),
                status_code=401,
                mimetype="application/json",
            )

        # Parse interaction
        interaction = json.loads(body)

        # Route interaction
        response = router.route(interaction)

        return func.HttpResponse(
            json.dumps(response),
            status_code=200,
            mimetype="application/json",
        )

    except json.JSONDecodeError:
        logger.error("Invalid JSON in request body")
        return func.HttpResponse(
            json.dumps({"error": "Invalid JSON"}),
            status_code=400,
            mimetype="application/json",
        )

    except Exception as e:
        logger.error(f"Unexpected error in interactions endpoint: {str(e)}", exc_info=True)
        return func.HttpResponse(
            json.dumps({"error": "Internal server error"}),
            status_code=500,
            mimetype="application/json",
        )


@app.route(route="health", methods=["GET"])
async def health_check(req: func.HttpRequest) -> func.HttpResponse:
    """Health check endpoint."""
    return func.HttpResponse(
        json.dumps({"status": "ok"}),
        status_code=200,
        mimetype="application/json",
    )
