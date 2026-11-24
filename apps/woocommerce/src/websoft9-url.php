<?php

$wp_forwarded_https = (
    isset($_SERVER['HTTP_X_FORWARDED_PROTO'])
    && stripos($_SERVER['HTTP_X_FORWARDED_PROTO'], 'https') !== false
);

if ($wp_forwarded_https) {
    $_SERVER['HTTPS'] = 'on';
}

$wp_scheme = $wp_forwarded_https ? 'https' : 'http';
$wp_home = trim((string) getenv('WP_HOME'));
$wp_siteurl = trim((string) (getenv('WP_SITEURL') ?: $wp_home));

if ($wp_home !== '' && !defined('WP_HOME')) {
    $wp_home_url = preg_match('#^https?://#i', $wp_home)
        ? rtrim($wp_home, '/')
        : $wp_scheme . '://' . rtrim($wp_home, '/');
    define('WP_HOME', $wp_home_url);
}

if ($wp_siteurl !== '' && !defined('WP_SITEURL')) {
    $wp_site_url = preg_match('#^https?://#i', $wp_siteurl)
        ? rtrim($wp_siteurl, '/')
        : $wp_scheme . '://' . rtrim($wp_siteurl, '/');
    define('WP_SITEURL', $wp_site_url);
}
