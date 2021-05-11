# myenergi2mqtt
Python daemon to publish Zappi status to mqtt broker


To run: 

Donwload the zip archive

Install dependencies:

```
pip3 install paho-mqtt requests lockfile python-daemon PyYAML
```

In the folder:
Make the main python executable: 


```
chmod 755 myenergi2mqtt.py
```

Create a config:

```
cp cfg.yaml.sample cfg.yaml
nano cfg.yaml

```

Execute: 

```
./myenergi2mqtt.py cfg.yaml
```

