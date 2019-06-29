===============================================
Welcome to Binance Chain Signing Service v0.0.4
===============================================

Features
--------

- Signing methods for Order, Cancel Order, Transfer, Freeze and Unfreeze tokens
- Sign and broadcast methods for above messages
- Resync a wallet to the chain
- Fetch wallet permissions and information such as address and environment
- Validated config using `pydantic <https://pydantic-docs.helpmanual.io/>`_
- `JWT <https://jwt.io/>`_ authentication method
- Multiple wallet support
- Create wallets with mnemonic or private_key
- Multiple user support
- Per wallet and per user permissions
- Users may have access to multiple wallets
- Individual Wallets specify environment, production or testnet
- Simple yaml configuration
- Supported by `python-binance-chain <https://github.com/sammchardy/python-binance-chain/>`_ python client library
  - This provides a simple error free client interface
- Native `OpenAPI <https://swagger.io/docs/specification/about/>`_ support
- Import OpenAPI schema into `Postman <https://www.getpostman.com/>`_ directly
- Auto generated `OpenAPI <https://swagger.io/docs/specification/about/>`_ documentation and JSON schema for building client interfaces.
- Fast server using next generation python 3 libraries `FastApi <https://github.com/tiangolo/fastapi>`_, `uvicorn <https://www.uvicorn.org/>`_ and `Starlette <https://github.com/encode/starlette>`_
- Docker support for ultimate portability
- Terraform example running on AWS Fargate behind ALB
- Lightweight, can run on Raspberry Pi
- Uses pydantic `Secret Types <https://pydantic-docs.helpmanual.io/#secret-types>`_ module to avoid leakage of private content
including private keys, password hashes and auth secret keys
- Passwords stored as hashes in the system
- Some IP whitelisting has been implemented
    - would recommend external security control if hosting on cloud services or through a proxy like Traefik or Nginx

Read the `Changelog <changelog.rst>`_

Test Service
------------

View the OpenAPI docs here `binance-signing-service.xyz <https://binance-signing-service.xyz/docs>`_

Import the OpenAPI schema to Postman from here `binance-signing-service.xyz <https://binance-signing-service.xyz/api/openapi.json>`_

Use https://binance-signing-service.xyz as the endpoint to communicate if you're using the `python-binance-chain <https://github.com/sammchardy/python-binance-chain/>`_ python client library.

Login credentials are

 - username: sam
 - password: mypass


Configuration
-------------

Modify the `config/config.yml` configuration file to include the wallets and users you need.

The configuration has 3 sections

**General**

.. code:: yaml

    # amount of minutes access tokens are valid, set to a large number if a long expiry is needed
    access_token_expiry_minutes: 10080
    # secret key to encode tokens, generate with a bcrypt tool
    secret_key: <bcrypt_hash>

**Wallets**

.. code:: yaml

    wallets:
      # the private key for this wallet
      - private_key: <private_key>
        # name of the wallet, this is used in requests to the signing service
        name: wallet_1
        # specify the environment to use for this wallet
        env_name: TESTNET  # or PROD
        ip_whitelist:  # optional section
          - 127.0.0.1
          - 10.0.0.1
        permissions:  # limit of permissions that users may be able to perform on this
          - trade
          - transfer

      # initialise wallet with mnemonic
      - mnemonic: '<mnemonic word string>'
        env_name: TESTNET
        name: wallet_2
        permissions:
          - transfer
          - freeze

    # add other wallets as needed

**Users**

.. code:: yaml

    users:
      - username: sam
        password_hash: <bcrypt_password_hash> # generate with online tool or command line

        # list of wallet permissions this user has
        wallet_permissions:
          # the wallet name from the wallets list above
          - wallet_name: wallet_1
            # perissions here are a subset of the wallet permissions
            permissions:
              - trade
              - transfer
          - wallet_name: wallet_2
            permissions:
              - transfer

If the user has trade permission but the wallet doesn't, then the wallet permission denies trade access.

**Permissions**

trade - allow order create and canceld
transfer - allow the transfer of funds from one account to another
freeze - allow freezing and unfreezing tokens
resync - allow resynchronising sequence info for the wallet

Wallets can have any combination of permissions to restrict access per wallet and per user.

Combined with multiple users you have the most flexibility in how accounts are accessed and used.

**Bcrypt Generation**

Some parts of the config require password hashes or just random strings to keep things secure.

Try `Bcrypt-Generator.com <https://bcrypt-generator.com/>`_ or the command line if you're more advance.


Running the server locally
------------------------------

This requires python 3.6+ and this setup

.. code:: bash

    # create an environment to use
    python3 -v venv .venv
    source .venv/bin/activate

    # install the requirements
    pip install -r app/requirements.txt

Run the server

.. code:: bash

    cd app

    uvicorn main:app --reload

If having issues with secp256k1 check the `Installation instructions for the sec256k1-py library <https://github.com/ludbb/secp256k1-py#installation>`_


Running the server with Docker
------------------------------

There is a sample Dockerfile available based on the `tiangolo/uvicorn-gunicorn-fastapi <https://github.com/tiangolo/uvicorn-gunicorn-fastapi-docker>`_ container.
See the `container docs <https://github.com/tiangolo/uvicorn-gunicorn-fastapi-docker>`_ for more configuration options.

The `/app` and `/config` directories are copied into the container.

To run it in Docker, build and run the container. Feel free to change `bdex-sign` and `bdex-sign-c` to your own
image and container names.

.. code:: bash

    docker build -t bdex-sign ./
    docker run -d --name bdex-sign-c -p 8001:80 bdex-sign

To check the log output

.. code:: bash

    docker logs bdex-sign-c

To stop the container

.. code:: bash

    docker stop bdex-sign-c

Finally to remove the container

.. code:: bash

    docker rm bdex-sign-c

Running the server more securely with Docker
--------------------------------------------

I would recommend using the `container with Traefik <https://github.com/tiangolo/medium-posts/tree/master/docker-swarm-mode-and-traefik-for-a-https-cluster>`_
to include Let's Encrypt support to serve content over HTTPS.

By running in an environment like AWS using ECS, one could point API Gateway to the instance and define IP whitelisting in this way.

Terraform
---------

A Terraform config for running the container in AWS Fargate with an ALB can be found in the `terraform` directory.

After pushing your build docker container to ECR you are nearly ready to go.

To do that

- create an ECR repository in AWS

- tag your local image with the repository name

.. code:: bash

    docker tag bdex-sign <account_id>.dkr.ecr.us-east-1.amazonaws.com/bdex-sign

- push the image to the repository

.. code:: bash

    docker push <account_id>.dkr.ecr.us-east-1.amazonaws.com/bdex-sign


Update `terraform/variables.tf` and fill in your aws_profile, container location and ecs_task_execution_role (it will
look something like arn:aws:iam::<account_id>:role/ecsTaskExecutionRole.

Now initialise terraform

.. code:: bash

    terraform init terraform/

Then apply the terraform plan

.. code:: bash

    terraform apply terraform/

This will output the URL to access your signing service.

To delete at any time

.. code:: bash

    terraform destroy terraform/


Authentication
--------------

**POST /api/auth/login**

Pass username and password payload to the endpoint to generate a JWT token to use for subsequent requests.

By default tokens expire after 7 days, this can be changed in the config.yml.

*Request*

.. code:: json

    {
        "username": "sambot",
        "password": "don'tforgetthis"
    }

*Response*

.. code:: json

    {
        "access_token": "eyJ0eXAiOiJKV1Qi....",
        "token_type": "bearer"
    }

Message Interaction
-------------------

All other endpoints require JWT token for authentication. Add this as a request header.

.. code:: yaml

    Authorization: Bearer <access_token>


**POST /api/order/sign**

Sign a new order message object and return the hash

Requires permission - trade

*Request*

.. code:: json

    {
        "msg": {
            "order_type": "LIMIT",
            "price": 0.000396,
            "quantity": 10,
            "side": "buy",
            "symbol": "ANN-457_BNB",
            "time_in_force": "GTE"
        },
        "wallet_name": "wallet_1"
    }

*Response*

.. code:: json

    {
        "signed_msg": "de01f0625dee0a6..."
    }

**POST /api/order/broadcast**

Sign a new order message object and return the exchanges response

Requires permission - trade

*Request*

Same as /api/order/sign

*Response*

Is the response from the Binance Chain exchange


**POST /api/cancel_order/sign**

Sign a cancel order message object and return the hash

Requires permission - trade

*Request*

.. code:: json

    {
        "msg": {
            "order_id": "<order_id>",
            "symbol": "ANN-457_BNB"
        },
        "wallet_name": "wallet_1"
    }

*Response*

.. code:: json

    {
        "signed_msg": "de01f0625dee0a6..."
    }

**POST /api/order/broadcast**

Requires permission - trade

Sign a cancel order message object and return the exchanges response

*Request*

Same as /api/cancel_order/sign

*Response*

Is the response from the Binance Chain exchange


**POST /api/transfer/sign**

Requires permission - transfer

Sign a transfer message object and return the hash

*Request*

.. code:: json

    {
        "msg": {
            "symbol": "BNB",
            "amount": 1,
            "to_address": "<to address>"
        },
        "wallet_name": "wallet_1"
    }

*Response*

.. code:: json

    {
        "signed_msg": "de01f0625dee0a6..."
    }

**POST /api/transfer/broadcast**

Requires permission - transfer
Sign a transfer message object and return the exchanges response

*Request*

Same as /api/transfer/sign

*Response*

Is the response from the Binance Chain exchange


**POST /api/freeze/sign**

Requires permission - freeze

Sign a freeze message object and return the hash

*Request*

.. code:: json

    {
        "msg": {
            "symbol": "BNB",
            "amount": 1,
        },
        "wallet_name": "wallet_1"
    }

*Response*

.. code:: json

    {
        "signed_msg": "de01f0625dee0a6..."
    }

**POST /api/freeze/broadcast**

Sign a transfer message object and return the exchanges response

Requires permission - freeze

*Request*

Same as /api/freeze/sign

*Response*

Is the response from the Binance Chain exchange


**POST /api/unfreeze/sign**

Sign an unfreeze message object and return the hash

Requires permission - freeze

*Request*

.. code:: json

    {
        "msg": {
            "symbol": "BNB",
            "amount": 1,
        },
        "wallet_name": "wallet_1"
    }

*Response*

.. code:: json

    {
        "signed_msg": "de01f0625dee0a6..."
    }

**POST /api/unfreeze/broadcast**

Sign an unfreeze message object and return the exchanges response

Requires permission - freeze

*Request*

Same as /api/unfreeze/sign

*Response*

Is the response from the Binance Chain exchange

Wallet Interaction
------------------

**POST /api/wallet/resync**

Resynchronise the wallet on the signing service. This can happen if the sequence gets out of order.

Requires permission - resync

*Request*

.. code:: json

    {
        "wallet_name": "wallet_1"
    }

*Response*

.. code:: json

    {}

**GET /api/wallet**

Fetch all wallet info the currently authorised user has access to

Requires permission - none

*Response*

.. code:: json

    [
        {
            "name": "wallet_1",
                "permissions": [
                "transfer",
                "trade"
            ],
            "env": "TESTNET",
            "address": "tbnb10a6kkxlf823w9lwr6l9hzw4uyphcw7qzrud5rr",
            "public_key": "02cce2ee4e37dc8c65d6445c966faf31ebfe578a90695138947ee7cab8ae9a2c08"
        },
        {
            "name": "wallet_2",
            "permissions": [
                "transfer"
            ],
            "env": "TESTNET",
            "address": "tbnb10a6kkxlf823w9lwr6l9hzw4uyphcw7qzrud5rr",
            "public_key": "02cce2ee4e37dc8c65d6445c966faf31ebfe578a90695138947ee7cab8ae9a2c08"
        }
    ]

**GET /api/wallet/{wallet_name}**

Fetch wallet info for the named wallet and the currently authorised user

Requires permission - none

*Response*

.. code:: json

    {
        "name": "wallet_1",
            "permissions": [
            "transfer",
            "trade"
        ],
        "env": "TESTNET",
        "address": "tbnb10a6kkxlf823w9lwr6l9hzw4uyphcw7qzrud5rr",
        "public_key": "02cce2ee4e37dc8c65d6445c966faf31ebfe578a90695138947ee7cab8ae9a2c08"
    }

Docs & OpenAPI
--------------

**/docs**

View the OpenAPI docs for this service and interact with it.

**/redoc**

View the docs in Redoc format

**/api/openapi.json**

Retrieve the OpenAPI JSON Schema for this service.

You can also import this directly into `Postman <https://www.getpostman.com/>`_


Using python-binance-chain
--------------------------

`python-binance-chain <https://github.com/sammchardy/python-binance-chain/>`_ has been updated to include this
signing service interface as an option to process messages

Initialise the client to interact with your signing service

.. code:: python

    from binance_chain.signing.http import HttpSigningClient
    from binance_chain.messages import NewOrderMsg

    signing_client = HttpSigningClient(url="http://localhost:8000", username="username", password="password")

    # create the message object
    new_order_msg = NewOrderMsg(
        symbol='ANN-457_BNB',
        order_type=OrderType.LIMIT,
        side=OrderSide.BUY,
        price=0.000396000,
        quantity=10,
        time_in_force=TimeInForce.GOOD_TILL_EXPIRE
    )

    # get hex data for a message
    new_order_hex = signing_client.sign_order(new_order_msg, wallet_name='wallet_1')

    # broadcast a message directly
    new_order_res = signing_client.broadcast_order(new_order_msg, wallet_name='wallet_1')
