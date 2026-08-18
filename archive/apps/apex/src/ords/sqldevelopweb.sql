BEGIN
 ords_admin.enable_schema(
  p_enabled => TRUE,
  p_schema => 'pdbadmin',
  p_url_mapping_type => 'BASE_PATH',
  p_url_mapping_pattern => 'admin',
  p_auto_rest_auth => TRUE
 );
 commit;
END;
