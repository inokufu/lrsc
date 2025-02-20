# LRSC -- Learning Record Store Connector

This project allows you to simultaneously deploy three components:
- **LRS (LearningLocker)**
- **LRSC (LRS Connector)** – which enables the PDC to interact with the LRS
- **PDC (PTX Dataspace Connector)**

This document outlines the steps to install, configure, and launch the project in a production environment.

---

## Table of Contents

- [Global Configuration](#global-configuration)
- [LearningLocker (LL) Configuration](#learninglocker-ll-configuration)
- [PDC (PTX Dataspace Connector) Configuration](#pdc-ptx-dataspace-connector-configuration)
- [Building and Launching the Project](#building-and-launching-the-project)
- [Post-Configuration for LearningLocker](#post-configuration-for-learninglocker)
- [Testing the LRSC](#testing-the-connection-between-the-lrsc-and-the-lrs)
- [Updating PDC Credentials](#post-configuration-for-the-pdc)
  - [Using the Swagger](#using-the-swagger)
  - [Using the Console](#using-the-console)
- [VisionsTrust Catalog : Configure a Data/Service Resource](#configure-a-data-or-service-resource-in-the-visionstrust-catalog)
- [Final Notes](#final-notes)
- [License](#license)

---

## Global Configuration

1. **DNS Records:** Ensure that the three required A records are set up for LRS, PDC, and LRSC applications.
2. **Environment File:**
    - Copy `.env.default` to `.env` in the project root:
        ```bash
        cp .env.default .env
        ```
    - Modify the necessary values :
        - `LL_DOMAIN_NAME`,
        - `LRSC_DOMAIN_NAME`,
        - `PDC_DOMAIN_NAME`,
        - `LETSENCRYPT_EMAIL`,
        - `LL_ORGANIZATION_NAME`,
        - `LL_MASTER_PASSWORD`.

---

## LearningLocker (LL) Configuration

1. Copy the default environment file:
   ```bash
   cp ll/.env.default ll/.env
   ```
2. Modify the configuration as needed.  
**Important:** You must at least change the `APP-SECRET` env variable in the `ll/.env` file.

---

## PDC (PTX Dataspace Connector) Configuration

1. Copy the sample configuration file:
   ```bash
   cp pdc/config.sample.json pdc/config.production.json
   ```
2. Edit `config.production.json`:
   - Fill in the first three fields (`endpoint`, `serviceKey`, `secretKey`).
   - For the last field (`credentials.0.value`): if the LRS is already available, fill it in with the Authorization header given by your LRS; otherwise, we will update it later.

---

## Building and Launching the Project

1. **Build the Project:**
   ```bash
   make build
   ```
   *Note: The build process may take between 1 and 20 minutes depending on your hardware.*

2. **Launch the Project:**
   ```bash
   ENV=prod make up
   ```

3. **Complete LearningLocker Initialization:**
   ```bash
   make ll-init
   ```

---

## Post-Configuration for LearningLocker

1. **Login the your LearningLocker instance:**  
   To log in, use `<<LL_MASTER_EMAIL>>` and `<<LL_MASTER_PASSWORD>>` environment variables.
2. **Create a Store:**  
   To create a store, enter your organization. Then, move to `Settings->Stores`, and click on `+Add New`.
   Creating a `Store` will automatically create a `Client`.
3. **Retrieve the Basic Auth Token:**  
   In the newly created `Client`, retrieve the token (hereafter referred to as `<<BASIC_TOKEN>>`).

---

## Testing the connection between the LRSC and the LRS

Make a test request to your LRS Connector using `curl`:

```bash
curl \
   --location 'https://<<LRSC_DOMAIN_NAME>>/statements?xapi_version=<<XAPI_VERSION>>&xapi_endpoint=<<LL_ENDPOINT>>' \
   --header 'Authorization: <<BASIC_TOKEN>>'
```

**Note:** The `LL_ENDPOINT` must be the URL to the xAPI entry point. For LearningLocker, it is typically: `https://<<LL_DOMAIN_NAME>>/data/xAPI/statements`. For a LRS such as ralph, it would be `https://<<LL_DOMAIN_NAME>>/xAPI/statements`.

**Example:**

```bash
curl \
   --location 'https://lrsc.test.inokufu.space/statements?xapi_version=1.0.3&xapi_endpoint=https://lrs.test.inokufu.space/data/xAPI/statements' \
   --header 'Authorization: <<BASIC_TOKEN>>'
```

---

## Post-Configuration for the PDC

By default, the PDC application can load credentials from the `config.json` (or `config.production.json`) file. In our case, it comes with empty credentials (an `apiKey` type) that needs to be updated with the `<<BASIC_TOKEN>>` obtained from LearningLocker.

You can update the credentials using one of the following methods:

### Using the Swagger

1. **Access the Swagger UI:**  
   Open your PDC instance in a browser at: `https://<<PDC_DOMAIN_NAME>>/docs`
2. **Login:**
   - Scroll down to the login route.
   - Submit a POST request containing your `<<SERVICE_KEY>>` and `<<SECRET_KEY>>` (available in the Catalog).  
      This request will return a token (`<<JWT_TOKEN>>`).
3. **Authorize:**
   - Copy the `<<JWT_TOKEN>>`.
   - Scroll back to the top of the Swagger, and click on the **Authorize** button in the top right corner.
   - Paste the token in the `jwt` field and click **Authorize**.
4. **Update Credentials:**
   - Scroll down to the **Update Credentials** route.
   - Submit the following PUT request (replace `<<BASIC_TOKEN>>` with your actual token):
     - **Credential ID:** `67375ec5f29f0c5a15265de5`.
     - **Request Body:**
       ```json
       {"type": "apiKey", "key": "Authorization", "value": "<<BASIC_TOKEN>>"}
       ```

### Using the Console

1. **Retrieve the JWT Token:**
   ```bash
   curl 'https://<<PDC_DOMAIN_NAME>>/login' \
     -X 'POST' \
     -H 'Content-Type: application/json' \
     --data '{"serviceKey": "<<SERVICE_KEY>>", "secretKey": "<<SECRET_KEY>>"}'
   ```
   *Extract the `<<JWT_TOKEN>>` from the response (`response->content->token`).*

2. **Update the Credential:**
   ```bash
   curl 'https://<<PDC_DOMAIN_NAME>>/private/credentials/67375ec5f29f0c5a15265de5' \
       -X 'PUT' \
       -H 'Authorization: Bearer <<JWT_TOKEN>>' \
       --data '{"type": "apiKey", "key": "Authorization", "value": "<<BASIC_TOKEN>>"}'
   ```

---

## Configure a Data or Service Resource in the VisionsTrust Catalog

- **Create a `Data (Service) Resource`.**
- In the **Personal Data** section, check the `Personal Data` box.
- In the **Tech** section:
  - **Data Representation**
    1. **Source Type:** `REST`
    2. **URL:**  
       `https://<<LRSC_DOMAIN_NAME>>/statements?xapi_version=<<XAPI_VERSION>>&xapi_endpoint=<<LL_ENDPOINT>>&agent={userId}`  
       **Example:**  
       `https://lrsc.test.inokufu.space/statements?xapi_version=1.0.3&xapi_endpoint=https://lrs.test.inokufu.space/data/xAPI/statements&agent={userId}`  
       **Note:** Ensure that you include the agent query parameter (`{userId}`) toe enable personal data exchanges.
  - **Security**
    1. **Select:** `Api-Key`
    2. **Credential Identifier:** `67375ec5f29f0c5a15265de5`  
       (This corresponds to the PDC credential containing the LearningLocker `<<BASIC_TOKEN>>` authentication.)
- **Validate the creation of the resource.**

---

## Final Notes

- **Ensure all domain names and tokens are correctly replaced** in the commands and configuration files.
- This setup assumes all components are running in production mode.
- For any issues or questions, please refer to the project documentation or contact the maintainers.

---

## License

This project is open source and distributed under the [MIT License](LICENSE.md).
