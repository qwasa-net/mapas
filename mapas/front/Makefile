O5_URL ?= https://github.com/qwasa-net/o5/releases/download/b470813/o5.linux.amd64
O5 ?= ./o5

build: build_tools www/index.html

build_tools: ./node_modules/.bin $(O5)

./node_modules/.bin:
	npm install

$(O5):
	curl --location "$(O5_URL)" -o "$(O5)"
	chmod 755 "$(O5)"

www/index.html: www www/media src/mapas.html.template www/mapas.min.css www/mapas.min.js www/svg-pan-zoom.min.js
	"$(O5)" -w ./ -i src/mapas.html.template -o www/index.html

www/mapas.min.js: src/mapas.js
	./node_modules/.bin/terser \
	--config-file terser.json \
	src/mapas.js \
	--output www/mapas.min.js

www/mapas.min.css: src/mapas.css
	./node_modules/.bin/cleancss \
	src/mapas.css \
	--output www/mapas.min.css

www/svg-pan-zoom.min.js: vendor/svg-pan-zoom-master/dist/svg-pan-zoom.min.js
	cp vendor/svg-pan-zoom-master/dist/svg-pan-zoom.min.js www/svg-pan-zoom.min.js

www:
	mkdir -pv ./www

www/media:
	cp -rv ./media ./www
