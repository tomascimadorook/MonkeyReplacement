#docker cp /Users/Shared/MonkeyReplacement/meli_raw.xls running-monkey:/usr/src/app/meli_raw.xls
docker cp /Users/Shared/MonkeyReplacement/ImageSrc/monkey.py running-monkey:/usr/src/app/monkey.py

docker exec -it running-monkey python /usr/src/app/monkey.py
docker cp running-monkey:/usr/src/app/processed_data_parquerodo.xls /Users/Shared/MonkeyReplacement/
open /Users/Shared/MonkeyReplacement/processed_data_parquerodo.xls
