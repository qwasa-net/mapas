/* eslint-disable valid-jsdoc, camelcase, guard-for-in */

const app = {

    // states of the game
    // (1) init → (2)
    // (2) new → (3)
    // (3) loading → (3)
    // (4) ready → (5)
    // (5) clicked → (5,6)
    // (6) posting → (7)
    // (7) end → (2)
    state: null, // game state

    // current task
    task: null,
    clicked_xy: [0, 0, 0, 0],
    tm_new_game: null,

    // page elements
    els: {
        'container': null,
        'canvas': null,
        'task': null,
        'answer': null,
        'send': null,
        'next': null,
        'state': null,
    },

    // svg-pan-zoom instance
    pz: null,

    init: function() {
        for (const el_id in this.els) {
            const el = document.getElementById(el_id);
            if (!el) {
                this.die(`error: ${el_id} does not exist!`);
            }
            this.els[el_id] = el;
        }
        this.change_game_state('init');

        // pointer
        this.pointer = get_pointer(this.els.container, 'real');
        this.pointer.add_click_haldler((e) => { this.pointer_clicked(e); }, 'dblclick');

        // set canvas loader handler
        this.els.canvas.addEventListener('load', (e) => { this.setup_panzoom(); });

        // second pointer
        this.helper = get_pointer(this.els.container, 'helper');

        // [GO] button
        this.els.send.addEventListener('click', (e) => { this.send_clicked(e); });

        // [NEXT] button
        this.els.next.addEventListener('click', (e) => { this.next_clicked(e); });

        // start!
        this.new_game();
    },

    new_game: function() {
        // reset things
        this.change_game_state('new');

        // ready to load
        this.load_game();
    },

    load_game: function() {
        this.change_game_state('loading');

        // fetch a task
        const req = {
            method: 'GET',
            cache: 'no-cache',
            mode: 'same-origin',
            credentials: 'same-origin',
        };

        fetch('/api/task', req)
            .then((rsp) => rsp.json())
            .then((data) => {
                if (data && data.id) {
                    this.task = data;
                    this.mapa = data.mapa;
                    this.show_game();
                } else {
                    this.die('invalid data');
                }
            })
            .catch((err) => { this.die(err); });
    },

    show_game: function() {
        // show task (game loaded)
        this.change_game_state('ready');
    },

    mapa_clicked: function(e) {
        if (!(this.state == 'ready' || this.state == 'clicked')) {
            this.put_pointers();
            return;
        }

        const ex = e.pageX;
        const ey = e.pageY;
        this.clicked_xy = this.from_canvas_point(ex, ey);

        this.change_game_state('clicked');
    },

    post_game: function() {
        // post game data (button/pointer clicked)
        if (this.state != 'clicked' && this.clicked_xy) {
            return false;
        }

        this.change_game_state('posting');

        const data = {
            'x': this.clicked_xy[2],
            'y': this.clicked_xy[3],
            'mapa_id': this.mapa.id,
            'task_id': this.task.id,
        };

        const req = {
            method: 'POST',
            cache: 'no-cache',
            mode: 'same-origin',
            credentials: 'same-origin',
            headers: { 'Content-Type': 'application/json' },
            redirect: 'follow',
            referrerPolicy: 'origin',
            body: JSON.stringify(data),
        };

        fetch('/api/answer', req)
            .then((rsp) => {
                rsp.json().then((data) => {
                    this.task.answer = data;
                    this.end_game();
                });
            })
            .catch((err) => { this.die(err); });
    },

    end_game: function() {
        this.change_game_state('end');
        this.tm_new_game = setTimeout((e) => { this.new_game(); }, 8000);
    },

    put_pointer: function(el, x0, y0) {
        const screenxy = this.to_canvas_point(x0 || el.x0, y0 || el.y0);
        el.moveto(screenxy[0], screenxy[1]);
    },

    put_pointers: function() {
        this.put_pointer(this.pointer);
        this.put_pointer(this.helper);
    },

    from_canvas_point: function(clickx, clicky) {
        const sizes = this.pz.getSizes();
        const pan = this.pz.getPan();
        const x = (clickx - pan.x - sizes.viewBox.x) / sizes.realZoom;
        const y = (clicky - pan.y - sizes.viewBox.y) / sizes.realZoom;
        const w = (this.mapa.w || sizes.viewBox.width || 360);
        const h = (this.mapa.h || sizes.viewBox.height || 180);
        const x0 = (x) / w;
        const y0 = (y) / h;
        console.log('@from_canvas_point', w, h, clickx, clicky, sizes, pan, x, y, '=>', x0, y0);
        return [x, y, x0, y0];
    },

    to_canvas_point: function(x0, y0) {
        const sizes = this.pz.getSizes();
        const pan = this.pz.getPan();
        const w = (this.mapa.w || sizes.viewBox.width || 360);
        const h = (this.mapa.h || sizes.viewBox.height || 180);
        const sx = (x0 * w) * sizes.realZoom + sizes.viewBox.x + pan.x;
        const sy = (y0 * h) * sizes.realZoom + sizes.viewBox.y + pan.y;
        console.log('@to_canvas_point', w, h, sizes, pan, x0, y0, '=>', sx, sy);
        return [sx, sy];
    },

    pointer_clicked: function(e) {
        console.log('@pointer_clicked', e);
        this.post_game();
    },

    send_clicked: function(e) {
        console.log('@pointer_clicked', e);
        this.post_game();
    },

    next_clicked: function(e) {
        console.log('@next_clicked', e);
        if (this.state == 'end') {
            this.new_game();
        }
    },

    setup_panzoom: function() {
        // reset pan zoom
        if (this.pz) {
            this.pz.destroy();
            delete this.pz;
        }

        const appa = this;
        const customEventsHandler = {
            init: function(o) { o.svgElement.addEventListener('click', this.mapa_clicked); },
            destroy: function(o) { o.svgElement.removeEventListener('click', this.mapa_clicked); },
            mapa_clicked: function(e) { appa.mapa_clicked(e); },
        };

        const svgpanzoom_options = {
            panEnabled: true,
            controlIconsEnabled: false,
            zoomEnabled: true,
            dblClickZoomEnabled: true,
            mouseWheelZoomEnabled: true,
            preventMouseEventsDefault: false,
            zoomScaleSensitivity: 0.3,
            minZoom: 0.25,
            maxZoom: 25,
            fit: true,
            contain: false,
            center: true,
            refreshRate: 'auto',
            customEventsHandler: customEventsHandler,
            onZoom: function(e) { appa.put_pointers(); },
            // onPan: function(e) { appa.put_pointers(); },
        };

        this.pz = svgPanZoom(this.els.canvas, svgpanzoom_options);
        this.pz.updateBBox();
        this.pz.resetZoom();
        this.pz.resize();
        this.pz.fit();
        this.pz.center();
    },

    change_game_state: function(state) {
        // set labels, show/hide controls

        const oldstate = this.state;
        this.state = state;
        console.log('@change_game_state', state);
        try { this.els.state.innerText = this.state; } catch (e) {}

        this.els.container.classList.remove(oldstate);
        this.els.container.classList.add(state);

        switch (state) {
            case 'new':

                clearTimeout(this.tm_new_game);

                this.els.next.classList.add('hidden');
                this.els.send.classList.add('hidden');

                this.els.answer.innerText = '';
                this.els.answer.classList.add('hidden');
                this.els.answer.classList.remove('good');
                this.els.answer.classList.remove('bad');

                this.els.task.innerText = '';
                this.els.task.classList.add('hidden');

                // reset pointers
                this.pointer.hide();
                this.pointer.moveto(this.els.container.clientWidth / 5, this.els.container.clientHeight / 5);
                this.helper.hide();
                this.helper.moveto(0, 0);

                break;

            case 'loading':
                break;

            case 'ready':

                // show task
                this.els.task.innerText = this.task.text;
                this.els.task.classList.remove('hidden');

                // load svg
                if (this.els.canvas.getAttribute('src') != this.task.mapa.path) {
                    console.log('loading svg', this.task.mapa.path);
                    this.els.canvas.setAttribute('src', this.task.mapa.path);
                } else {
                    console.log('reuse svg', this.task.mapa.path);
                    this.setup_panzoom();
                }

                break;

            case 'clicked':
                this.pointer.show();
                this.pointer.set_xy0(this.clicked_xy[2], this.clicked_xy[3]);
                this.helper.set_xy0(this.clicked_xy[2], this.clicked_xy[3]);
                this.put_pointers();
                this.els.send.classList.remove('hidden');
                break;

            case 'posting':
                this.els.send.classList.add('hidden');
                this.helper.show();
                break;

            case 'end':
                const data = this.task.answer;

                this.helper.show();
                this.els.answer.innerText = '~' + String(Math.round(data.distance || 0)) + 'km';
                this.els.answer.classList.remove('hidden');
                this.els.next.classList.remove('hidden');

                const score = Number(data.score);
                if (score === 1) {
                    this.els.answer.classList.add('good');
                } else if (score === 0) {
                    this.els.answer.classList.add('bad');
                }

                let screenxy = this.to_canvas_point(data.x, data.y);
                console.log('screenxy', screenxy);
                if (screenxy[0] < 0 || screenxy[1] < 0 ||
                    screenxy[0] > this.els.container.clientWidth || screenxy[1] > this.els.container.clientHeight) {
                    this.pz.fit();
                    this.pz.center();
                    screenxy = this.to_canvas_point(data.x, data.y);
                }
                this.helper.set_xy0(data.x, data.y);
                this.put_pointers();

                break;
        }
    },

    die: function(err) {
        console.log(err);
        window.location.replace('about:blank');
    },

};

/**
 * Build pointer object (div).
 * @param {el} parent The parent node.
 * @param {string} klass Element's class.
 * @returns {element} The pointer.
 */
function get_pointer(parent, klass, handler) {
    const p = {

        el: null,
        x: 0,
        y: 0,
        offx: 0,
        offy: 0,
        x0: 0,
        y0: 0,

        init: function(klass) {
            this.el = document.createElement('div');
            this.el.classList.add('pointer');
            if (klass) {
                this.el.classList.add(klass);
            }
            const svg = this.draw(klass);
            this.el.appendChild(svg);
            return this.el;
        },

        attach: function(parent) {
            parent.appendChild(this.el);
            this.offx = this.el.offsetWidth / 2;
            this.offy = this.el.offsetHeight / 2;
        },

        add_click_haldler: function(handler, ev) {
            this.el.addEventListener(ev || 'click', handler);
        },

        set_xy: function(x, y) {
            this.x = x;
            this.y = y;
        },

        set_xy0: function(x0, y0) {
            this.x0 = x0;
            this.y0 = y0;
        },

        moveto: function(x, y) {
            x = x || this.x || 0;
            y = y || this.y || 0;
            this.el.style.left = (x - this.offx) + 'px';
            this.el.style.top = (y - this.offy) + 'px';
        },

        hide: function() {
            this.el.classList.add('hidden');
        },

        show: function() {
            this.el.classList.remove('hidden');
        },

        draw: function() {
            const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
            svg.setAttributeNS(null, 'viewBox', '0 0 100 100');
            const ball = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
            ball.setAttributeNS(null, 'id', 'ball');
            ball.setAttributeNS(null, 'class', 'ballb');
            ball.setAttributeNS(null, 'cx', 50);
            ball.setAttributeNS(null, 'cy', 50);
            ball.setAttributeNS(null, 'r', 45);
            const ball2 = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
            ball2.setAttributeNS(null, 'id', 'balls');
            ball2.setAttributeNS(null, 'class', 'balls');
            ball2.setAttributeNS(null, 'cx', 50);
            ball2.setAttributeNS(null, 'cy', 50);
            ball2.setAttributeNS(null, 'r', 20);
            svg.appendChild(ball);
            svg.appendChild(ball2);
            return svg;
        },

    };

    p.init(klass);
    if (parent) {
        p.attach(parent);
    }
    if (handler) {
        p.add_click_haldler(handler);
    }

    return p;
};

// init on load
window.addEventListener('load', (e) => { app.init(); });
