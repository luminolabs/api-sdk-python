# Deploying to PyPI

Follow the steps below to deploy the api_sdk package to PyPI.

---

### 1. Create an API Key

First, create an API key on [PyPI](https://pypi.org/). This key will be used for authentication during deployment.

### 2. Set Up `.pypirc` Configuration

Next, create a `.pypirc` file in your home directory (`~/.pypirc`) with the following content. This file is needed to authenticate and upload your package to PyPI.

```bash
[distutils]
  index-servers =
    lumino

[lumino]
  repository = https://upload.pypi.org/legacy/
  username = __token__
  password = <API_KEY>
```

Replace <API_KEY> with the actual API key you created in step 1.

### 3. Update the VERSION File

Ensure the VERSION file is updated with the correct version before deploying.

### 4. Deploy the Package

Once everything is set, deploy to PyPI by running the following script:

```bash
./scripts/push-to-pypi.sh
```

Check the [PyPI page](https://pypi.org/project/lumino/) to verify that the package has been successfully deployed.

You’re all set! 