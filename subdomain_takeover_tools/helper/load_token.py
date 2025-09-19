from azure.identity import DefaultAzureCredential

def load_token():
    credential = DefaultAzureCredential()
    (token, _) = credential.get_token('https://management.azure.com/.default')