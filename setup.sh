mkdir -p ~/.streamlit/

echo "\
[general]\n\
email = \"medicalaudit@protecthealth.com.my\"\n\
" > ~/.streamlit/credentials.toml

echo "\
[server]\n\
headless = true\n\
port = $PORT\n\
enableCORS = false\n\
\n\
" > ~/.streamlit/config.toml