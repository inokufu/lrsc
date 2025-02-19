from logging import basicConfig, getLogger, INFO
from typing import Any, Dict, List

from fastapi import Depends, FastAPI, HTTPException, Query, Request
from fastapi.responses import JSONResponse
from pydantic import AnyHttpUrl, BaseModel
from requests import get as requests_get, post as requests_post
from urllib.parse import urlparse, urlencode

basicConfig(level=INFO)
logger = getLogger(__name__)

XAPI_ENDPOINT = 'xapi_endpoint'
XAPI_VERSION = 'xapi_version'


class InputQueryModel(BaseModel):
    xapi_endpoint: AnyHttpUrl = Query(min_length=1)
    xapi_version: str = Query(min_length=1)


app = FastAPI(
    title="LRS Connector",
    description="LRS Connector is a lightweight FastAPI application designed to act as a proxy for querying Learning Record Stores (LRS) such as Learning Locker or Ralph, from the DataSpace.",
    version="0.0.1",
)

@app.get("/statements", tags=["statements"])
async def get_statements(request: Request, query: InputQueryModel = Depends()):
    # Extract headers
    headers = {key: value for key, value in request.headers.items() if key.lower() != 'host'}
    headers["X-Experience-API-Version"] = query.xapi_version
    
    # Extract query parameters
    query_params = {key: value for key, value in request.query_params.items() if key not in [XAPI_ENDPOINT, XAPI_VERSION]}
    query_string = urlencode(query_params)

    try:
        # Parse the xAPI endpoint
        parsed_url = urlparse(str(query.xapi_endpoint))

        # Extract the base URL and the base path
        lrs_base_url = parsed_url.scheme + "://" + parsed_url.netloc
        xapi_base_path = parsed_url.path

        # Build the URL dynamically
        api_url = f"{lrs_base_url}{xapi_base_path}" + (f"?{query_string}" if query_string else "")
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

@app.post("/statements", tags=["statements"])
async def post_statement(request: Request, payload: List[Dict[Any, Any]], query: InputQueryModel = Depends()):
    # Extract headers
    headers = {key: value for key, value in request.headers.items() if key.lower() != 'host'}
    headers["X-Experience-API-Version"] = query.xapi_version

    # Send the POST request to the LRS
    try:
        response = requests_post(url=query.xapi_endpoint, headers=headers, json=payload)
        response.raise_for_status()
    except Exception as e:
        logger.error("Couldn't post data to the LRS: %s", e)
        raise HTTPException(status_code=500, detail="Couldn't post data to the LRS") from e

    return JSONResponse(content=response.json())
