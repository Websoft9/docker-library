# CHANGELOG

## 2026-11-09

- Added a Symfony 8.1 runtime package using PHP 8.5 FrankenPHP and an initialized starter application.
- Fixed the starter app returning 404 on `/` caused by a production cache copied from the scaffold temp directory, and warm up the cache at container start.
- Added a default `public/favicon.ico` so browsers no longer fall back to the red-cross icon from Symfony's error page.
