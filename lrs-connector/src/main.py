from logging import basicConfig, getLogger, INFO
from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.responses import JSONResponse
from pydantic import AnyHttpUrl
from requests import get as requests_get
from urllib.parse import urlparse, urlencode

basicConfig(level=INFO)
logger = getLogger(__name__)

XAPI_ENDPOINT = 'xapi_endpoint'
XAPI_VERSION = 'xapi_version'

app = FastAPI(
    title="LRS Connector",
    description="LRS Connector is a lightweight FastAPI application designed to act as a proxy for querying Learning Record Stores (LRS) such as Learning Locker or Ralph, from the DataSpace.",
    version="0.0.1",
)

@app.get("/statements", tags=["statements"])
async def get_statements(request: Request, xapi_endpoint: AnyHttpUrl = Query(min_length=1), xapi_version: str = Query(min_length=1)):
    # Extract headers and query parameters
    headers = {key: value for key, value in request.headers.items() if key.lower() != 'host'}
    headers["X-Experience-API-Version"] = xapi_version
    query_params = {key: value for key, value in request.query_params.items() if key not in [XAPI_ENDPOINT, XAPI_VERSION]}
    query_string = urlencode(query_params)

    try:
        # Parse the xAPI endpoint
        parsed_url = urlparse(str(xapi_endpoint))

        # Extract the base URL and the base path
        lrs_base_url = parsed_url.scheme + "://" + parsed_url.netloc
        xapi_base_path = parsed_url.path

        # Build the URL dynamically
        api_url = f"{lrs_base_url}{xapi_base_path}" + (f"?{query_string}" if query_string else "")
        logger.debug("Built the URL: %s", api_url)
    except Exception as e:
        logger.error("Couldn't build the URL: %s", e)
        raise HTTPException(status_code=500, detail="Couldn't build the URL") from e

    accumulated_statements = []
    # Fetch data from the LRS, paginating if necessary
    while api_url:
        # Fetch data from the LRS
        try:
            response = requests_get(url=api_url, headers=headers)
            response.raise_for_status()
        except Exception as e:
            logger.error("Couldn't fetch data from the LRS: %s", e)
            raise HTTPException(status_code=500, detail="Couldn't fetch data from the LRS") from e

        # Parse the response
        try:
            fetched_data = response.json()
            accumulated_statements.extend(fetched_data.get("statements", []))
            more = fetched_data.get("more")
            api_url = more if more and more.startswith("http") else f"{lrs_base_url}{more}" if more else None
        except Exception as e:
            logger.error("Couldn't parse the response from the LRS: %s", e)
            raise HTTPException(status_code=500, detail="Couldn't parse the response from the LRS") from e

    return JSONResponse(accumulated_statements)
