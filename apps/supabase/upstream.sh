# upstream from supabase

git clone --depth=1 https://github.com/supabase/supabase.git    source
yes | cp -rf source/docker/volumes/*  ./src
rm -rf source