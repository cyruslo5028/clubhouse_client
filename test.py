from ytmusicapi import YTMusic
header_="""accept: */*
accept-encoding: gzip, deflate, br
accept-language: en-US,en;q=0.9
authorization: SAPISIDHASH 1616271523_1f780107646447bd905c3269ef5edd2974ab3a2a
content-length: 766
content-type: application/json
cookie: VISITOR_INFO1_LIVE=deljJFjN_Ok; LOGIN_INFO=AFmmF2swRgIhALMxB88-Ow1Ge8onrUN12umRt4JJPTisNBydlpelFEzNAiEAiWB0JNAHYxSq6YZpqp96obvRufqGKmmswwFRYTD4ynE:QUQ3MjNmejF1VXRaaGtWdm9uNVhobU50bWZwT2Z5aVlPeEY3Y3lQTk0yRXc2ajJuQ0RTTUJpRXYycF9Ec1lWOWl4VlZrWVlJdG9VMElvcURmb0p3SVZ1S0JPYmN6S1ZrYmZCSi1aTjhjT29rM244UzJvN1ZhbURVZWFuNGFuSmNUU1laLUVUNlNobEpvb05Xa2RrVFdKWTlqVllINXdXb0tBX2xuRkFTQW94UEpBVGZuck40d1NZ; HSID=Ak0zW8l5upXUDzgiu; SSID=ANEfZ7fqtUzYWAxz2; APISID=4QFSV-mDfoBw3qoN/Aq-EBZKxnW8WvdOWi; SAPISID=Wb7Fm6fCyB1uvP81/A7Ss0m0CLukBrHHcC; __Secure-3PAPISID=Wb7Fm6fCyB1uvP81/A7Ss0m0CLukBrHHcC; YSC=-qTPz9ffs_o; wide=1; _gcl_au=1.1.408840996.1615174770; SID=7gcfLK3Hk5NSXbBk4_rQptRVteuLyWgEXam6JK6c3GxA89iuvuwecNfvkN2yo_LmB-vtyA.; __Secure-3PSID=7gcfLK3Hk5NSXbBk4_rQptRVteuLyWgEXam6JK6c3GxA89iuAOQXeP2xbnKt0qEi7nG2Zg.; PREF=f6=80&volume=0&tz=America.Los_Angeles&library_tab_browse_id=FEmusic_library_corpus_artists&location_based_recommendations=1&al=zh-TW&f5=30; SIDCC=AJi4QfGhOZ5vbQdTbL8W7FYKGIcwDvx-rgeobyE5dmfiwO-BSb9NBB9K5A687ivoVuc0yIAPuM8; __Secure-3PSIDCC=AJi4QfFTBJWQc4AMgbLBJH9qwGSgQhTV_JEiGgFsR80B1_WOBEptomL5SUlKqEqAsXurDOX6iNk6
origin: https://music.youtube.com
referer: https://music.youtube.com/
sec-ch-ua: "Google Chrome";v="89", "Chromium";v="89", ";Not A Brand";v="99"
sec-ch-ua-mobile: ?0
sec-fetch-dest: empty
sec-fetch-mode: cors
sec-fetch-site: same-origin
user-agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.90 Safari/537.36
x-client-data: CJS2yQEIpLbJAQjEtskBCKmdygEIlqzKAQiIucoBCPjHygEI28/KAQjN+8oBCLKaywEI5JzLAQiPncsBCKidywEIzp/LAQ==
Decoded:
message ClientVariations {
  // Active client experiment variation IDs.
  repeated int32 variation_id = [3300116, 3300132, 3300164, 3313321, 3315222, 3316872, 3318776, 3319771, 3325389, 3329330, 3329636, 3329679, 3329704, 3329998];
}
x-goog-authuser: 0
x-goog-pageid: undefined
x-goog-visitor-id: CgtkZWxqSkZqTl9PayiisdmCBg%3D%3D
x-origin: https://music.youtube.com
x-youtube-ad-signals: dt=1616271522259&flash=0&frm&u_tz=-420&u_his=2&u_java&u_h=1440&u_w=5120&u_ah=1360&u_aw=5120&u_cd=24&u_nplug=3&u_nmime=4&bc=31&bih=1280&biw=1236&brdim=1324%2C96%2C1324%2C96%2C5120%2C25%2C1685%2C1360%2C1248%2C1280&vis=1&wgl=true&ca_type=image
x-youtube-client-name: 67
x-youtube-client-version: 0.1
x-youtube-device: cbr=Chrome&cbrand=apple&cbrver=89.0.4389.90&ceng=WebKit&cengver=537.36&cos=Macintosh&cosver=11_2_1&cplatform=DESKTOP&cyear=2013
x-youtube-identity-token: QUFFLUhqazFrNDc1QlVmU3FMRWIwRFE4SERSanAzMVpYd3w=
x-youtube-page-cl: 362928533
x-youtube-page-label: youtube.music.web.client_20210315_00_RC00
x-youtube-time-zone: America/Los_Angeles
x-youtube-utc-offset: -420"""
YTMusic.setup(filepath=headers_auth.json)