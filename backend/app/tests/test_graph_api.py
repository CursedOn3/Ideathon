from app.integrations.graph_api import publish_to_sharepoint

def test_publish():
    res = publish_to_sharepoint("123")
    assert res["status"] == "published"
