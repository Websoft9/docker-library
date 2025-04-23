# Zerotier

This is Zerotier client docker image. 

- If use host network mode, your host machine will add to vitual network of zerotier
- If use container network(e.g websoft9), your container will add to vitual network of zerotier

## Prepare

This applicaiton need your register account at [my.zerotier.com](https://my.zerotier.com/), and create a vitual network and get the **Network ID**.

Then,you can install it at Websoft9 AppStore, and enter the **Network ID** when install.

## Quickstart

1. Register account at [my.zerotier.com](https://my.zerotier.com/) and create a vitual network and get the **Network ID**
2. Install Zerotier from at Websoft9 AppStore where need to input **Network ID** before installation
3. Logint to [my.zerotier.com](https://my.zerotier.com/) and [Authorize your device on your network](https://docs.zerotier.com/start/#authorize-your-device-on-your-network)
4. Get **Managed IPs** of your device from **my.zerotier.com** console, and connect each other by this IPs

## Option

- check your client connection from container: `zerotier-cli listnetworks`

## FAQ
