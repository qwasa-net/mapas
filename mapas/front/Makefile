EXPANDER ?= cat


build: install_tools www/index.html


install_tools: node_modules/.bin
node_modules/.bin:
	npm install


www/index.html: www www/media src/mapas.html.template www/mapas.min.css www/mapas.min.js www/svg-pan-zoom.min.js
	$(EXPANDER) src/mapas.html.template > www/index.html


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
	mkdir -pv www


www/media:
	cp -rv media www
