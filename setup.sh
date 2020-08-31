mkdir -p ~/.streamlit/                                               

echo "\
[general]\n\
email = \"michal.frankl@gmail.com\"\n\
" > ~/.streamlit/credentials.toml

echo "\
[server]\n\
port = $PORT\n\
enableCORS = false\n\
headless = true\n\
" > ~/.streamlit/config.toml