Changelog
=========

v0.0.4 - 2019-04-16
^^^^^^^^^^^^^^^^^^^

**Added**

- memo field to transfer endpoint

v0.0.2 - 2019-04-16
^^^^^^^^^^^^^^^^^^^

**Added**

- Sample server at `binance-signing-service.xyz <https://binance-signing-service.xyz/docs>`_
- Terraform example running on AWS Fargate behind ALB

v0.0.1 - 2019-04-14
^^^^^^^^^^^^^^^^^^^

**Added**

- Signing methods for Order, Cancel Order, Transfer, Freeze and Unfreeze tokens
- Sign and broadcast methods for above messages
- Validated config using `pydantic <https://pydantic-docs.helpmanual.io/>`_
- `JWT <https://jwt.io/>`_ authentication method
- Multiple wallet support
- Multiple user support
- Per wallet and per user permissions
- Users may have access to multiple wallets
- Individual Wallets specify environment, production or testnet
- Simple yaml configuration
- Supported by `python-binance-chain <https://github.com/sammchardy/python-binance-chain/>`_ python client library
  - This provides a simple error free client interface
- Native `OpenAPI <https://swagger.io/docs/specification/about/>`_ support
- Auto generated `OpenAPI <https://swagger.io/docs/specification/about/>`_ documentation and JSON schema for building client interfaces.
- Fast server using next generation python 3 libraries `FastApi <https://github.com/tiangolo/fastapi>`_, `uvicorn <https://www.uvicorn.org/>`_ and `Starlette <https://github.com/encode/starlette>`_
- Docker support for ultimate portability
- Lightweight, can run on Raspberry Pi
- Uses pydantic `Secret Types <https://pydantic-docs.helpmanual.io/#secret-types>`_ module to avoid leakage of private content
including private keys, password hashes and auth secret keys
- Passwords stored as hashes in the system
