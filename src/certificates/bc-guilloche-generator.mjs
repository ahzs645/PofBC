// Geometry is in the 722 × 550 coordinate system of the reference image.
const pitch = 42.35;
const half = pitch / 2;
const format = value => String(Number(value.toFixed(3)));
const pointText = p => p.map(format).join(' ');
const mix = (a, b, t) => [a[0] + t*(b[0]-a[0]), a[1] + t*(b[1]-a[1])];
const reverse = array => array.slice().reverse();

function guide(startY, ...segments) {
  let start = [0, startY];
  return segments.map(([bx, by, cx, cy, dx, dy]) => {
    const curve = [start, [bx, by], [cx, cy], [dx, dy]];
    start = curve[3];
    return curve;
  });
}

const guides = {
  rail: guide(14.3,[8,14.15,11.1,18.25,16,19.5],[18,20.03,19.6,20.35,half,20.27]),
  welt: guide(15.75,[8.8,15.75,12,20.5,16.8,21.4],[18.4,21.75,20,21.9,half,21.87]),
  outer: guide(17.7,[10.4,17.6,15.1,24.95,half,34.9]),
  fan: guide(27.7,[6.45,27.35,11.15,31.7,15.15,38.1],[17.05,41.3,19,42.1,half,42.2]),
  swell: guide(37.9,[6.25,37.4,9.6,43.35,14.2,45.75],[18.25,48.1,19.5,45.55,half,45.75]),
  lip: guide(41.95,[6.7,41.3,9.05,44.55,11,49.7],[14.1,51.4,17.2,51.25,18.8,49.6],[19.8,48.9,20.7,48.6,half,48.55]),
  hood: guide(41.7,[7.1,41.38,11.8,45.1,12.15,55.4],[12,57,14.2,57.9,16.7,55.15],[19,54,20.6,53.1,half,53.1]),
  arch: guide(52.2,[5.8,52.25,6.6,56.85,7.45,63.8],[10.7,62.45,14.6,56.7,half,56.8]),
  foot: guide(72.9,[6.5,72.9,14,72.9,half,72.9]),
  capBase: guide(41.88,[5.85,41.15,9.2,44.6,12.8,47.8],[17.1,51.9,19.2,47.75,half,47.7])
};

function inset(key, dy, side = 0) {
  return guides[key].map(curve => curve.map(([x, y]) =>
    [x - side * Math.sin(Math.PI*x/half), y + dy]));
}
Object.assign(guides, {
  rimGap: inset('outer',-1.75), fanIn: inset('fan',1.24,.63),
  swellIn: inset('swell',1.26,.72), hoodIn: inset('hood',.8,.86),
  lipIn: inset('lip',.86,.56), archIn: inset('arch',1.16,.79)
});

// Sampling in arc length keeps the strands evenly distributed around a lobe.
function arcProfile(curves) {
  const points = [], lengths = [];
  let length = 0;
  for (const [a,b,c,d] of curves) {
    for (let i=0; i<120; i++) {
      const t = i/119, s = 1-t;
      const p = [0,1].map(k => s**3*a[k]+3*s*s*t*b[k]+3*s*t*t*c[k]+t**3*d[k]);
      const last = points[points.length-1];
      if (last) length += Math.hypot(p[0]-last[0], p[1]-last[1]);
      points.push(p);
      lengths.push(length);
    }
  }
  return {points, lengths, length};
}
const profiles = Object.fromEntries(Object.entries(guides).map(([key,value]) => [key, arcProfile(value)]));
function atPhase(name, u) {
  const {points, lengths, length} = profiles[name];
  const cycle = Math.floor(u+.5), phase = u-cycle;
  const target = 2*Math.abs(phase)*length;
  let low=0, high=lengths.length-1;
  while (high-low>1) {
    const middle = (low+high) >>> 1;
    if (lengths[middle]<=target) low=middle;
    else high=middle;
  }
  const span = lengths[high]-lengths[low];
  const [x,y] = mix(points[low],points[high],span ? (target-lengths[low])/span : 0);
  return [cycle*pitch+(phase<0 ? -x : x), y];
}
function wholeGuide(key) {
  const halfGuide = guides[key];
  return [...reverse(halfGuide).map(c => reverse(c).map(([x,y]) => [-x,y])), ...halfGuide];
}
function trace(curves, start='M') {
  return start+pointText(curves[0][0])+curves.map(c => 'C'+c.slice(1).map(pointText).join(' ')).join('');
}
function ribbon(a,b) {
  return trace(wholeGuide(a))+trace(reverse(wholeGuide(b)).map(reverse),'L')+'Z';
}

// Each strand is an outlined Bézier ribbon. Sample both edges so that changes
// in coverage follow the local spacing as the weave travels through a bend.
function weavePaths(outer, inner, count, coverage, twist, bulge) {
  const paths = [];
  for (const sign of [-1,1]) {
    for (let i=Math.floor(-count/2)-5; i<=Math.floor(count/2)+5; i++) {
      const u=i/count, offset=coverage/(2*count);
      function atDepth(t, edge) {
        const phase=u+edge+sign*(t-.5)*twist+bulge*Math.sin(2*Math.PI*u)*Math.sin(Math.PI*t);
        return mix(atPhase(outer,phase),atPhase(inner,phase),t);
      }
      function side(from,to,edge) {
        let path='';
        for (let k=0;k<3;k++) {
          const lo=from+(to-from)*k/3, hi=from+(to-from)*(k+1)/3;
          const delta=Math.sign(hi-lo)*.00015, factor=(hi-lo)/(3*delta);
          const a=atDepth(lo,edge), b=atDepth(hi,edge);
          const ca=mix(a,atDepth(lo+delta,edge),factor);
          const cb=mix(b,atDepth(hi-delta,edge),factor);
          path+='C'+[ca,cb,b].map(pointText).join(' ');
        }
        return path;
      }
      paths.push('M'+pointText(atDepth(0,-offset))+side(0,1,-offset)+
                 'L'+pointText(atDepth(1,offset))+side(1,0,offset)+'Z');
    }
  }
  return paths.join('');
}

const group = (id,body) => `<g id="${id}">${body}</g>`;
const use = (id,x=0) => `<use xlink:href="#${id}" x="${format(x)}"/>`;
const clip = (id,path) => `<clipPath id="${id}">${path}</clipPath>`;
const clipped = (id,content) => `<g clip-path="url(#${id})">${content}</g>`;
const transpose = body => `<g transform="matrix(0 1 1 0 0 0)">${body}</g>`;

function repeatDefinitions(ink,density) {
  const stroke = (d,w) => `<path d="${d}" fill="none" stroke="${ink}" stroke-width="${format(w)}"/>`;
  const fill = d => `<path d="${d}" fill="${ink}"/>`;
  function weave(a,b,count,coverage,twist,bulge,edgeA,edgeB) {
    return fill(weavePaths(a,b,Math.round(count*density),coverage,twist,bulge))+
           stroke(trace(wholeGuide(a)),edgeA)+stroke(trace(wholeGuide(b)),edgeB);
  }
  let bands=group('scalloped-rules',stroke(trace(wholeGuide('rail')),.75)+stroke(trace(wholeGuide('welt')),.83));
  bands+=group('pierced-spandrels',clipped('rim-shoulders',fill(ribbon('welt','rimGap'))));
  bands+=group('outer-fan',weave('outer','fan',26,.532,.125,.017,.4,.31));
  bands+=group('middle-fan',weave('fanIn','swell',38,.405,.12,.016,.22,.25));
  bands+=group('dark-cap',fill(ribbon('swellIn','capBase'))+weave('capBase','lip',27,.42,.075,.008,.1,.12));
  bands+=group('shoulder-lace',weave('lipIn','hood',31,.4,.086,.01,.16,.18));
  bands+=group('inner-fan',weave('hoodIn','arch',36,.455,.112,.009,.27,.27));
  bands+=clipped('footcut',group('foot-lace',weave('archIn','foot',40,.425,.113,.008,.24,.18)));
  let bud=stroke('M-4.55 72.9 C-5.25 68.8 -4.4 61.95 0 61.65 C4.4 61.95 5.25 68.8 4.55 72.9',1.12);
  bud+=stroke('M-3.35 72.8 C-4.45 68.4 -2.75 63.6 0 63.45 C2.75 63.6 4.45 68.4 3.35 72.8',.44);
  for(let i=-3;i<=3;i++) {
    const x=i*.92;
    for(const bend of [1.2,-1.25]) {
      bud+=stroke('M'+pointText([x*.54,64.15+Math.abs(x)*.63])+'Q'+pointText([x*.75+bend,66.9])+' '+pointText([x*1.12,72.8]),.35);
    }
  }
  bud+=fill('M0 64.3 C-.45 65.3 -1.7 65.9 -1.55 66.95 Q0 66.4 1.55 66.95 C1.7 65.9 .45 65.3 0 64.3Z M-.25 69.2 Q0 66.4 .5 69.3 Q.9 71.6 2.5 72.9 H-2.5 Q-.7 71.1 -.25 69.2Z');
  const bow = "M-11 68.7 Q-9.6 66.1 -7.6 65.4 Q-6.8 62.95 -2.2 64.1 Q0 65.1 2.2 64.1 Q6.8 62.95 7.6 65.4 Q9.6 66.1 11 68.7 Q10 70.85 7.35 71.95 L7.75 73.05 H-7.75 L-7.35 71.95 Q-10 70.85 -11 68.7Z";
  const bowHoles = " M-6.2 66.35 Q-4.25 66.65 -2.75 68.15 Q-1.35 67.95 0 66.9 Q1.35 67.95 2.75 68.15 Q4.25 66.65 6.2 66.35 Q5.76 67.7 4.2 68.8 Q5.76 69.65 6.2 71.15 Q4.3 70.9 2.75 69.45 Q1.2 69.68 0 70.87 Q-1.2 69.68 -2.75 69.45 Q-4.3 70.9 -6.2 71.15 Q-5.76 69.65 -4.2 68.8 Q-5.76 67.7 -6.2 66.35Z M0 67.75 Q.86 68.1 1.72 68.8 Q.9 69.6 0 70.04 Q-.9 69.6 -1.72 68.8 Q-.86 68.1 0 67.75Z";
  for(const x of [-half,half]) {
    bud+=`<path transform="translate(${format(x)} 0)" d="${bow+bowHoles}" fill-rule="evenodd" fill="${ink}"/>`;
  }
  bands+=group('buds-and-bows',bud);
  let braid=stroke('M-22 73.55H22',1.18)+stroke('M-22 74.65H22',.6)+stroke('M-22 80.65H22',.62)+stroke('M-22 81.75H22',.95);
  const step=pitch/7;
  for(const sign of [-1,1]) {
    for(let i=-5;i<5;i++) {
      braid+=stroke('M'+pointText([i*step,77.65])+'c'+pointText([step/5,-2.85*sign])+' '+pointText([step*.32,-2.85*sign])+
        ' '+pointText([step/2,0])+'s'+pointText([step*.32,2.85*sign])+' '+pointText([step/2,0]),.59);
    }
  }
  braid+=stroke('M-22 75.65H22M-22 79.65H22',.66);
  for(let i=-5;i<5;i++) {
    const x=i*step;
    for(const shift of [0,step/2]) {
      braid+=stroke('M'+pointText([x+shift,77.55])+'q'+pointText([step*.23,-1.8])+' '+pointText([step/2,0])+'t'+pointText([step/2,0]),.55);
    }
    braid+=fill('M'+pointText([x-.4,77.5])+'l.4 -1.1 .45 1.1 -.45 1.1Z');
  }
  bands+=group('inner-braided-rule',braid);
  let rim='M-25 8H25V36H-25Z';
  for(const x of [-half,half]) rim+=' M'+pointText([x-3.05,22.75])+'q3.05 .9 6.1 0 q-1.15 2.6 -3.05 3.75 q-1.9 -1.15 -3.05 -3.75Z';
  return clip('unit-cut',`<rect x="${format(-half-.07)}" y="8" width="${format(pitch+.14)}" height="76"/>`)+
         clip('rim-shoulders',`<path clip-rule="evenodd" d="${rim}"/>`)+clip('footcut',`<path d="${"M-22 45H22V63.7 C19 64.2 16 62.2 13.6 65.4 Q11.4 66.2 10.2 68.7 Q11.4 71.3 13.8 72 L13.45 73.3 H4.45 C5.1 68.7 4.1 62.2 0 61.95 C-4.1 62.2 -5.1 68.7 -4.45 73.3 H-13.45 L-13.8 72 Q-11.4 71.3 -10.2 68.7 Q-11.4 66.2 -13.6 65.4 C-16 62.2 -19 64.2 -22 63.7 Z"}"/>`)+
         group('engraved-repeat',clipped('unit-cut',`<g transform="scale(1.0014 1)">${bands}</g>`));
}

function arm(id,span,phase,includeEnd=false) {
  let tiles='';
  for(let x=phase-2*pitch;x-half<span+(includeEnd ? .001 : 0);x+=pitch) tiles+=use('engraved-repeat',x);
  return clip(id+'-miter',`<path d="M0 0H${format(span)}V83H83Z"/>`)+group(id,clipped(id+'-miter',tiles));
}

/** Generate a self-contained SVG. Density 1 uses the certificate's reconstruction settings. */
function generateBorder({view='frame', corner='certificate', ink='#056a43', density=1}={}) {
  if (!['frame','corner','repeat'].includes(view)) throw new RangeError('Unknown view');
  if (!['certificate','long-leaf'].includes(corner)) throw new RangeError('Unknown corner');
  if (!/^#[a-f0-9]{6}$/i.test(ink)) throw new TypeError('Use a six-digit hex colour');
  if (!Number.isFinite(density) || density<.6 || density>1.5) throw new RangeError('Density must be between 0.6 and 1.5');
  const phase=corner==='long-leaf' ? 60.4 : 47.8;
  let defs=repeatDefinitions(ink,density);
  let box, body, title;
  if(view==='frame') {
    const width=715.2, height=549.4;
    defs+=arm('long-half',width/2,phase)+arm('short-half',height/2,phase);
    defs+=group('corner-to-midpoints',use('long-half')+transpose(use('short-half')));
    const parts=[[0,0,1,1],[width,0,-1,1],[width,height,-1,-1],[0,height,1,-1]];
    body='<g transform="matrix(1.0008 0.00045 0.0034 0.9996 2.82 0.36)">'+
      parts.map(([x,y,sx,sy])=>`<g transform="translate(${x} ${y}) scale(${sx} ${sy})">${use('corner-to-midpoints')}</g>`).join('')+'</g>';
    box=[0,0,722,550]; title='British Columbia training certificate border';
  } else if(view==='corner') {
    const size=phase+1.5*pitch;
    defs+=arm('corner-arm',size,phase,true);
    body=use('corner-arm')+transpose(use('corner-arm')); box=[0,0,size,size]; title='Guilloché corner';
  } else {
    body=use('engraved-repeat'); box=[-half,13.5,pitch,69]; title='Seamless guilloché repeat';
  }
  return `<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="${format(box[2])}" height="${format(box[3])}" viewBox="${box.map(format).join(' ')}"><title>${title}</title><desc>Procedural reconstruction of the 1961 certificate ornament.</desc><defs>${defs}</defs>${body}</svg>`;
}

export { generateBorder };
