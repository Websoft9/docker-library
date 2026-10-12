# openGauss

openGauss kernel was originally derived from PostgreSQL

## Config

- CLI: should `su - omm` change user to use them

   - client cli: `gsql`, 
   - server cli: `gs_ctl, gs_dump, gs_restore ...`

## Quick start

You install openGauss cli in container directly or [install it](https://docs.opengauss.org/zh/docs/6.0.0/docs/GettingStarted/%E4%BD%BF%E7%94%A8gsql%E8%AE%BF%E9%97%AEopenGauss.html) at your host machine.

1. Docker exec to container, run below command
   ```
   su - omm
   gsql -d postgres -U gaussdb
   ```

2. Input your db password for testing

## FAQ