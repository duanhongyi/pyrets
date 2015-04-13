pyrets
======

Using python3, it supports the login, search, getmetadata and logout transaction.

    import pyrets.session
    rets_session = pyrets.session.RetsSession(
        "http://brc.rebretstest.interealty.com/Login.asmx/Login",
        "RETS***",
        "****",
        "****/1.0",
        "***_",
        "RETS/1.7",
    )


    #login, login is required before you do any other transactions
    response_text = rets_session.login()
    print(response_text)

    #getmetadata
    metadata_text = rets_session.get_metadata()
    with open('./12meta.xml','w') as f:
        f.write(metadata_text)
    
    #getobject    
    object_bin = rets_session.getobject('Photo','Property','40621107:1')
	with open('./a.jpg', 'wb') as f:
	    f.write(object_bin)
	    
    #search
    response = rets_session.search("Property","2", "(217=2014-01-01T12:31:00Z+)")
    print(response)
	
    #logout
    response_text = rets_session.logout()  
    print(response_text)
