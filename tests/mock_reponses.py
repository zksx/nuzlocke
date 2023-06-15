class MockResponse:
    def __init__(self, json_data, status_code):
        self.json_data = json_data
        self.status_code = status_code

    def json(self):
        return self.json_data
    
# STATUS CODES
status_code = {
    "OK": 200,
}

# VIDEO LIST RESPONSE
json_v_l_data={
    "kind": "youtube#videoListResponse",
    "etag": "jEatulrisgO-NhOYoQL_6hrfKKE",
    "items": [
        {
        "kind": "youtube#video",
        "etag": "qoAJC006Esw3v79zt5IFysVTJ14",
        "id": "jfKfPfyJRdk",
        "liveStreamingDetails": 
        {
            "actualStartTime": "2022-07-12T15:59:30Z",
            "scheduledStartTime": "2022-07-12T16:00:00Z",
            "concurrentViewers": "37036",
            "activeLiveChatId": "Cg0KC2pmS2ZQZnlKUmRrKicKGFVDU0o0Z2tWQzZOcnZJSTh1bXp0ZjBPdxILamZLZlBmeUpSZGs"
        }
        }
    ],
    "pageInfo": 
    {
        "totalResults": 1,
        "resultsPerPage": 1
    }

    }

# LIVE CHAT MESSAGE LIST RESPONSE (STREAM ONLINE)
json_lcm_l_data={
    "kind": "youtube#liveChatMessageListResponse",
    "etag": "0lOplhRLRERA4ELR37NzmaA6Px0",
    "pollingIntervalMillis": 4802,
    "pageInfo": 
        {
        "totalResults": 71,
        "resultsPerPage": 1
        },
    "nextPageToken": "GJjzsISZwf8CIKPQ2byZwf8C",
    "items": 
        [
            {
                "kind": "youtube#liveChatMessage",
                "etag": "0UVKH468c3MUhnLkV_SKWwx64Qk",
                "id": "LCC.CjgKDQoLamZLZlBmeUpSZGsqJwoYVUNTSjRna1ZDNk5ydklJOHVtenRmME93EgtqZktmUGZ5SlJkaxIcChpDTHZEcjRTWndmOENGV3dKMWdBZElnWUt2UQ",
                "snippet": 
                    {
                    "type": "textMessageEvent",
                    "liveChatId": "Cg0KC2pmS2ZQZnlKUmRrKicKGFVDU0o0Z2tWQzZOcnZJSTh1bXp0ZjBPdxILamZLZlBmeUpSZGs",
                    "authorChannelId": "fake_channel_id",
                    "publishedAt": "2023-06-13T21:31:56.822936+00:00",
                    "hasDisplayContent": True,
                    "displayMessage": "fake msg text",
                    "textMessageDetails": 
                        {
                            "messageText": "fake msg text"
                        }
                    },
                "authorDetails": 
                    {
                        "channelId": "fake_channel_id",
                        "channelUrl": "http://www.youtube.com/channel/fake_channel_id",
                        "displayName": "fake display name",
                        "profileImageUrl": "profile image text",
                        "isVerified": False,
                        "isChatOwner": False,
                        "isChatSponsor": False,
                        "isChatModerator": False
                    }
            }
        ]
    }

json_lcm_l_data_offline={
    "kind": "youtube#liveChatMessageListResponse",
    "etag": "0lOplhRLRERA4ELR37NzmaA6Px0",
    "pollingIntervalMillis": 4802,
    "offlineAt": "2023-6-14 09:00:00",
    "pageInfo": 
        {
        "totalResults": 71,
        "resultsPerPage": 1
        },
    "nextPageToken": "GJjzsISZwf8CIKPQ2byZwf8C",
    "items": 
        [
            {
                "kind": "youtube#liveChatMessage",
                "etag": "0UVKH468c3MUhnLkV_SKWwx64Qk",
                "id": "LCC.CjgKDQoLamZLZlBmeUpSZGsqJwoYVUNTSjRna1ZDNk5ydklJOHVtenRmME93EgtqZktmUGZ5SlJkaxIcChpDTHZEcjRTWndmOENGV3dKMWdBZElnWUt2UQ",
                "snippet": 
                    {
                    "type": "textMessageEvent",
                    "liveChatId": "Cg0KC2pmS2ZQZnlKUmRrKicKGFVDU0o0Z2tWQzZOcnZJSTh1bXp0ZjBPdxILamZLZlBmeUpSZGs",
                    "authorChannelId": "fake_channel_id",
                    "publishedAt": "2023-06-13T21:31:56.822936+00:00",
                    "hasDisplayContent": True,
                    "displayMessage": "fake msg text",
                    "textMessageDetails": 
                        {
                            "messageText": "fake msg text"
                        }
                    },
                "authorDetails": 
                    {
                        "channelId": "fake_channel_id",
                        "channelUrl": "http://www.youtube.com/channel/fake_channel_id",
                        "displayName": "fake display name",
                        "profileImageUrl": "profile image text",
                        "isVerified": False,
                        "isChatOwner": False,
                        "isChatSponsor": False,
                        "isChatModerator": False
                    }
            }
        ]
    }

v_l_response = MockResponse(json_v_l_data,status_code["OK"])
lcm_l_response = MockResponse(json_lcm_l_data, status_code["OK"])
lcm_l_offline_resp = MockResponse(json_lcm_l_data_offline, status_code["OK"])

responses_dict = {
    "video list" : v_l_response,
    "live chat message list": lcm_l_response,
    "live chat message list offline": lcm_l_offline_resp
}
