(()=>{var F=class{el=void 0;constructor(i){this.el=i}traversals={first:"firstElementChild",next:"nextElementSibling",parent:"parentElement"};nodes(){return this.traversals={first:"firstChild",next:"nextSibling",parent:"parentNode"},this}first(){return this.teleportTo(this.el[this.traversals.first])}next(){return this.teleportTo(this.teleportBack(this.el[this.traversals.next]))}before(i){return this.el[this.traversals.parent].insertBefore(i,this.el),i}replace(i){return this.el[this.traversals.parent].replaceChild(i,this.el),i}append(i){return this.el.appendChild(i),i}teleportTo(i){return i&&(i._x_teleport?i._x_teleport:i)}teleportBack(i){return i&&(i._x_teleportBack?i._x_teleportBack:i)}};function o(a){return new F(a)}function H(a){let i=document.createElement("template");return i.innerHTML=a,i.content.firstElementChild}function L(a){return a.nodeType===3||a.nodeType===8}var j=()=>{},R=()=>{};async function g(a,i,v){let A,m,C,K,O,b,N,S,k,_,B;function d(e){if(!!B)return R((e||"").replace(`
`,"\\n"),A,m),new Promise(t=>j=()=>t())}function q(e={}){let t=p=>p.getAttribute("key"),n=()=>{};O=e.updating||n,b=e.updated||n,N=e.removing||n,S=e.removed||n,k=e.adding||n,_=e.added||n,C=e.key||t,K=e.lookahead||!1,B=e.debug||!1}async function M(e,t){if(z(e,t)){let p=G(e,t);return await d("Swap elements"),p}let n=!1;if(!y(O,e,t,()=>n=!0)){if(window.Alpine&&W(e,t,()=>n=!0),L(t)){await P(e,t),b(e,t);return}n||await I(e,t),b(e,t),await J(e,t)}}function z(e,t){return e.nodeType!=t.nodeType||e.nodeName!=t.nodeName||x(e)!=x(t)}function G(e,t){if(y(N,e))return;let n=t.cloneNode(!0);y(k,n)||(o(e).replace(n),S(e),_(n))}async function P(e,t){let n=t.nodeValue;e.nodeValue!==n&&(e.nodeValue=n,await d("Change text node to: "+n))}async function I(e,t){if(e._x_isShown&&!t._x_isShown||!e._x_isShown&&t._x_isShown)return;let n=Array.from(e.attributes),p=Array.from(t.attributes);for(let h=n.length-1;h>=0;h--){let c=n[h].name;t.hasAttribute(c)||(e.removeAttribute(c),await d("Remove attribute"))}for(let h=p.length-1;h>=0;h--){let c=p[h].name,l=p[h].value;e.getAttribute(c)!==l&&(e.setAttribute(c,l),await d(`Set [${c}] attribute to: "${l}"`))}}async function J(e,t){let n=e.childNodes,p=t.childNodes,h=V(p),c=V(n),l=o(t).nodes().first(),r=o(e).nodes().first(),w={};for(;l;){let u=x(l),f=x(r);if(!r)if(u&&w[u]){let s=w[u];o(e).append(s),r=s,await d("Add element (from key)")}else{let s=Q(l,e)||{};await d("Add element: "+(s.outerHTML||s.nodeValue)),l=o(l).nodes().next();continue}if(K){let s=o(l).next(),D=!1;for(;!D&&s;)r.isEqualNode(s)&&(D=!0,r=T(l,r),f=x(r),await d("Move element (lookahead)")),s=o(s).next()}if(u!==f){if(!u&&f){w[f]=r,r=T(l,r),w[f].remove(),r=o(r).nodes().next(),l=o(l).nodes().next(),await d('No "to" key');continue}if(u&&!f&&c[u]&&(r=o(r).replace(c[u]),await d('No "from" key')),u&&f){w[f]=r;let s=c[u];if(s)r=o(r).replace(s),await d('Move "from" key');else{w[f]=r,r=T(l,r),w[f].remove(),r=o(r).next(),l=o(l).next(),await d("Swap elements with keys");continue}}}let U=r&&o(r).nodes().next();await M(r,l),l=l&&o(l).nodes().next(),r=U}let E=[];for(;r;)y(N,r)||E.push(r),r=o(r).nodes().next();for(;E.length;){let u=E.shift();u.remove(),await d("remove el"),S(u)}}function x(e){return e&&e.nodeType===1&&C(e)}function V(e){let t={};return e.forEach(n=>{let p=x(n);p&&(t[p]=n)}),t}function Q(e,t){if(!y(k,e)){let n=e.cloneNode(!0);return o(t).append(n),_(n),n}return null}function T(e,t){if(!y(k,e)){let n=e.cloneNode(!0);return o(t).before(n),_(n),n}return t}return q(v),A=a,m=H(i),window.Alpine&&window.Alpine.closestDataStack&&!a._x_dataStack&&(m._x_dataStack=window.Alpine.closestDataStack(a),m._x_dataStack&&window.Alpine.clone(a,m)),await d(),await M(a,m),A=void 0,m=void 0,a}g.step=()=>j();g.log=a=>{R=a};function y(a,...i){let v=!1;return a(...i,()=>v=!0),v}function W(a,i,v){a.nodeType===1&&a._x_dataStack&&window.Alpine.clone(a,i)}function $(a){a.morph=g}document.addEventListener("alpine:init",()=>{window.Alpine.plugin($)});})();