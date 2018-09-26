# video-thumbnailer

```
docker build -t thumbnail .
```

```
docker run -v <path/to/video>:/docker/video -e input="<input-file-name>" -e output="<output-file-name>" thumbnail
```
