///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
// UTILITIES
///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

const MODIFIERS = [
    "defer",
    "lazy",
    "debounce"
]

const ATTRIBUTES = [
    "wire:model",
    "wire:poll",
    "wire:snapshot"
]

const print_ = console.log

const attrStartsWith = (prefix) =>
    Array.from(document.querySelectorAll('*'))
        .filter(
            (e) => Array.from(e.attributes).filter(
                ({name, value}) => name.startsWith(prefix)).length
        )

function strip_wire_item_from_el(el, attribute) {
    let parts;
    let raw_attribute
    let modifier;
    let time;
    let property;
    let value;


    parts = el.outerHTML.split(" ")
    parts.forEach(i => {
        if (i.startsWith(attribute)) {
            raw_attribute = i.split('=')[0]
            attribute = raw_attribute.split('.')[0]

            if (!attribute.split(':')[1].includes('model') || !attribute.split(':')[1].includes('poll') || !attribute.split(':')[1].includes('snapshot')) {
                modifier = attribute.split(':')[1]
            }

            if (attribute.includes('model')) {
                if (MODIFIERS.includes(replaceUndefinied(i.split('.')[1]).split('=')[0])) {
                    modifier = i.split('.')[1].split('=')[0]
                } else {
                    modifier = undefined
                }
            }


            if (replaceUndefinied(i.split('.')[2]).split('=')[0].endsWith('s')) {
                time = i.split('.')[2].split('=')[0]
            } else {
                time = undefined
            }

            property = el.getAttribute(raw_attribute)
            value = el.value
        }
    })
    return [attribute, raw_attribute, modifier, time, property, value]
}

function resolve(path, obj = self, separator = '.') {
    if (path.includes('undefined')) {
        path = path.split('.')[0]
    }
    let properties = Array.isArray(path) ? path : path.split(separator)
    let res = properties.reduce((prev, curr) => prev?.[curr], obj)
    if (typeof res === 'object') {
        return res[`${path.split('.')}`]
    } else {
        return res
    }
}

function replaceUndefinied(item) {
    var str = JSON.stringify(item, function (key, value) {
            return (value === undefined || value.includes('.')) ? "" : value
        }
    );
    return JSON.parse(str);
}


function parseInterval(str) {
    if (str === undefined) {
        return undefined
    }
    if (str.slice(-2) === "ms") {
        return parseFloat(str.slice(0, -2)) || undefined
    }
    if (str.slice(-1) === "s") {
        return (parseFloat(str.slice(0, -1)) * 1000) || undefined
    }
    if (str.slice(-1) === "m") {
        return (parseFloat(str.slice(0, -1)) * 1000 * 60) || undefined
    }
    return parseFloat(str) || undefined
}


var debounce = (function () {
    var timers = {};

    return function (callback, delay, id) {
        delay = delay || 500;
        id = id || "duplicated event";

        if (timers[id]) {
            clearTimeout(timers[id]);
        }

        timers[id] = setTimeout(callback, delay);
    };
})(); // note the call here so the call for `func_to_param` is omitted

///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
// INITIALIZERS
///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
document.querySelectorAll('[wire\\:snapshot]').forEach(el => {
    el.__livewire = JSON.parse(el.getAttribute('wire:snapshot'))
    init_wire_model(el)
    init_wire_poll(el)
    init_wire_event_delegator(el)
})


///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
// SERVER CALL
///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
function send_request(el, add_to_payload) {
    let snapshot = el.__livewire

    fetch("/mvlive", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({
            snapshot: snapshot,
            ...add_to_payload
        })
    }).then(i => i.json()).then(response => {
        let {html, snapshot} = response
        el.__livewire = snapshot
        Alpine.morph(el.firstElementChild, html, {
            morphStyle: 'innerHTML',
            key(el) {
                return el.id
            }
        })
        updateWireModelInputs(el)
    })
}


///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
// POLLING
///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
function init_wire_poll(el) {
        console.log(el);
        [attribute, raw_attribute, modifier, time, property, value] = strip_wire_item_from_el(el.firstElementChild, "wire:poll")
        console.log(attribute, raw_attribute, modifier, time, property, value)

        let method = i.getAttribute(raw_attribute) || 'render';

        if (raw_attribute.split(".")[1] === undefined) {
            time = "2s"
        } else {
            time = raw_attribute.split(".")[1]
        }


        (function () {
            setInterval(function () {
                send_request(el, {callMethod: method})
            }, parseInterval(time));
        })()

}


///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
// MODELING
///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
function init_wire_model(el) {
    updateWireModelInputs(el);
    [attribute, raw_attribute, modifier, time, property, value] = strip_wire_item_from_el(el, "wire:model")

    const debounceModel = _.debounce((el, payload) => {
        send_request(el, payload);
    }, parseInterval(time))


    el.addEventListener('input',
        e => {

            let attribute;
            let raw_attribute
            let value;
            let property;
            let modifier;
            let time;

            [attribute, raw_attribute, modifier, time, property, value] = strip_wire_item_from_el(e.target, "wire:model")
            if (modifier === 'lazy') return;
            if (modifier === 'defer') return;
            if (modifier === 'debounce') {
                if (time === undefined) {
                    time = "1s"
                }

                debounceModel(el, {update_property: [property, value]});
            } else {
                send_request(el, {update_property: [property, value]})
            }

        }
    )


    el.addEventListener('change',
        e => {
            let attribute;
            let raw_attribute
            let value;
            let property;
            let modifier;
            let time;

            [attribute, raw_attribute, modifier, time, property, value] = strip_wire_item_from_el(e.target, "wire:model")
            if (modifier === undefined) return;
            if (modifier === 'defer') return;
            if (modifier === 'debounce') return;
            send_request(el, {update_property: [property, value]})
        }
    )


}

function updateWireModelInputs(el) {
    let data = el.__livewire.data

    attrStartsWith('wire:model').forEach(e => {
        [attribute, raw_attribute, modifier, time, property, value] = strip_wire_item_from_el(e, "wire:model")
    })
}


///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
// EVENTS - DELEGATOR
///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
function init_wire_event_delegator(el) {
    [attribute, raw_attribute, modifier, time, property, value] = strip_wire_item_from_el(el.children[0], "wire:")
    if (ATTRIBUTES.includes(attribute)) return;

    el.addEventListener(modifier, function (e) {

        let attribute, raw_attribute, modifier, time, property, value
        [attribute, raw_attribute, modifier, time, property, value] = strip_wire_item_from_el(e.target, "wire:")

        if (MODIFIERS.includes(modifier) || modifier === undefined) {

        } else {
            value = e.target.getAttribute(raw_attribute)
            send_request(el, {'callMethod': JSON.stringify(value)})
        }

    })


}

