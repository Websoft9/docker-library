# Apache Traffic Server

## Notes

- Default HTTP port: 8080
- Default HTTPS port: 8443
- Management interface: 8088
- Configuration files are mounted from `./src/` directory
- Cache storage is persistent across container restarts

## Configuration Notes

1. **Reverse Proxy Setup**: Edit `src/remap.config` to configure backend server mappings
2. **Performance Tuning**: Modify `src/records.config` for cache size and connection limits
3. **SSL Configuration**: Place SSL certificates in the appropriate volume mount if needed

## Troubleshooting

### Common Issues

1. **"Not Found on Accelerator" Error**: 
   - Check that remap.config has correct mapping rules
   - Ensure the client URL matches the mapping pattern
   - Verify that the origin server in remap.config is accessible

2. **Container fails to start**: Check port conflicts (8080, 8443, 8088)
3. **Configuration errors**: Validate syntax in `records.config`, `records.yaml` and `remap.config`
4. **Permission issues**: Ensure proper file permissions for mounted configuration files

### Logs

- Access logs: `/var/log/trafficserver/access.log`
- Error logs: `/var/log/trafficserver/error.log`
- Manager logs: `/var/log/trafficserver/manager.log`

## FAQ

### Q: How to configure TrafficServer as a reverse proxy?
A: Edit the `src/remap.config` file and add mapping rules like:
```
map http://your-domain.com/ http://backend-server:port/
```

### Q: How to increase cache size?
A: Modify the following lines in `src/records.config`:
```
CONFIG proxy.config.cache.ram_cache.size INT 268435456  # RAM cache in bytes
CONFIG proxy.config.cache.disk_space INT 10737418240     # Disk cache in bytes
```

### Q: How to enable HTTPS?
A: Configure SSL certificates and update the SSL settings in `records.config`

### Q: How to monitor TrafficServer?
A: Use the management interface at `http://your-server:8088/` or check the log files
