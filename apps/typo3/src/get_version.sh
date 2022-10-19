echo "typo3 version:" $(docker exec -i $1 grep "'version' => '" typo3_src/typo3/sysext/beuser/ext_emconf.php |awk -F">" '{print$2}' ) 1>> /data/logs/install_version.txt
