from azure.identity import DefaultAzureCredential


def load_token():
    credential = DefaultAzureCredential()
    (my_token, _) = credential.get_token('https://management.azure.com/.default')
    return my_token
