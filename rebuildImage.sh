docker stop running-monkey
docker rm running-monkey
docker rmi monkey
cd /Users/Shared/MonkeyReplacement/ImageSrc
docker build -t monkey .
