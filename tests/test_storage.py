from trendbolt_mcp.storage.azure_blob import AzureBlobClient


def test_azure_blob_client_has_methods():
    c = AzureBlobClient.__init__
    # Smoke test presence of methods without importing Azure modules
    assert hasattr(AzureBlobClient, "upload_bytes")
    assert hasattr(AzureBlobClient, "generate_sas_url")

