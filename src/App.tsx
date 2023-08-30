import React, { useState } from 'react';
import './App.css';

var color = "#000000"
var framelock = false
var lock = false

function stop() {
  lock = true;
}

const lights: string[] = []
let i = 0
while (i < 32) {
  lights.push(String(i));
  i++
}

type Frame = {
  duration: number,
  image: string[],
}

function makeChangeColor(id: string) {
  return () => document.getElementById(id)!.style.background=color;
}

type LightParam = {
  id: string
}

function Light(p: LightParam) {
  return (
    <button id={p.id}
    onClick={makeChangeColor(p.id)}
    style={{
      verticalAlign:"top",
      background: "#000000",
      height: 50,
      width: 50,
    }} />
  )
}

function LightingGrid() {
  return (
    <div>
      <table align="center" table-layout="fixed" style={{
        width: 650,
        borderSpacing: "50px"
      }}>
        <tr style={{
        }}>
          <td style={{
            transform:"rotate(45deg)",
            }}>
              <p>
                <Light id="0"/>
                <Light id="1"/>
                <Light id="2"/>
                <Light id="3"/>
                <br />
                <Light id="4"/>
                <Light id="5"/>
                <Light id="6"/>
                <Light id="7"/>
                <br />
                <Light id="8"/>
                <Light id="9"/>
                <Light id="10"/>
                <Light id="11"/>
                <br />
                <Light id="12"/>
                <Light id="13"/>
                <Light id="14"/>
                <Light id="15"/>
              </p>
          </td>
          <td style={{
            transform:"rotate(45deg)",
          }}>
            <p>
              <Light id="16"/>
              <Light id="17"/>
              <Light id="18"/>
              <Light id="19"/>
              <br />
              <Light id="20"/>
              <Light id="21"/>
              <Light id="22"/>
              <Light id="23"/>
              <br />
              <Light id="24"/>
              <Light id="25"/>
              <Light id="26"/>
              <Light id="27"/>
              <br />
              <Light id="28"/>
              <Light id="29"/>
              <Light id="30"/>
              <Light id="31"/>
            </p>
          </td>
        </tr>
      </table>
    </div>
  )
}

type ColorButtonParams = {
  color: string
}

function makeUseColor(c: string) {
  return () => {
    color = c;
  }
}

function ColorButton(props: ColorButtonParams) {
  return (
    <button id={props.color} style={{
      background: props.color,
      height: 50,
      width: 50,
    }}
    onClick={makeUseColor(props.color)} />
  )
}

function App() {
  const [looping, setLooping] = useState<boolean>(false)
  const [currFrame, setCurrFrame] = useState<number>(0)
  const [frames, setFrames] = useState<Frame[]>([{duration: 0, image:Array(32).fill("#000000")}]);
  const [colors, setColors] = useState<string[]>([
    "#000000",
    "#FFFFFF",
    "#FF0000",
    "#FFA500",
    "#FFFF00",
    "#00FF00",
    "#0000FF",
    "#FF00FF"
  ]);
  const  handleKeyDown = (event: React.KeyboardEvent) => {
    if (event.key === 'Enter') {
      saveFrame();
    }
  }
  async function play() {
    if (framelock) {
      return
    }
    lock = false
    for (var frame of frames) {
      if (lock) {
        break
      }
      for (let i = 0; i<32; i++) {
        document.getElementById(String(i))!.style.background = frame.image[i]
      }
      framelock = true
      await new Promise(resolve => setTimeout(resolve, frame.duration))
      framelock = false
    }
  }
  async function loop() {
    setLooping(!looping)
    if (frames[0].duration == 0){
      return
    }
    while (!looping && !framelock && !lock) {
      await play()
    }
  }
  function reset() {
    lights.map(id => document.getElementById(id)!.style.background="#000000")
  }
  function loadFrame(frameIndex: number) {
    return () => {
      let frame = frames[frameIndex]
      const input = document.getElementById("duration") as HTMLInputElement
      input.value = String(frame.duration)
      for (let i = 0; i<32; i++) {
        document.getElementById(String(i))!.style.background = frame.image[i]
      }
      setCurrFrame(frameIndex)
    }
  }
  function saveFrame() {
    
    const input = document.getElementById("duration") as HTMLInputElement
    console.log(input)
    let duration = parseInt(input.value)
    if (duration > 0) {
      console.log(lights)
      let image: string[] = lights.map(l => document.getElementById(l)!.style.background)
      frames[currFrame] = {duration:duration, image:image}
      if (currFrame + 1 == frames.length) {
        setCurrFrame(currFrame+1)
        frames.push({duration: 0, image:image})
        input.value = ""
      }
      setFrames([...frames])
      console.log(frames)
    }
    return
  }
  return (
    <div className="App">
        <LightingGrid />
      <div>
        {colors.map(color => <ColorButton color={color} />)}
        <button id="reset"
          onClick={reset}
          style={{
            verticalAlign:"top",
            background: "#999999",
            height: 50,
            width: 50,
          }}>reset</button>
      </div>
      <div>
        <input type="number"
          id="duration"
          onKeyDown={handleKeyDown}
          style={{height:45, width:90}}/>
        <button
          onClick={saveFrame}
          style={{
            background: "#999999",
            height: 50,
            width: 50,
          }}>save</button>
      </div>
      <div>
        <button onClick={play}
        style={{
          background: "#999999",
          height: 50,
          width: 50,
        }}>play</button>
        <button onClick={loop}
        style={{
          background: looping ? "#FF0000" : "#999999",
          height: 50,
          width: 50,
        }}>loop</button>
        <button onClick={stop}
        style={{
          background: "#999999",
          height: 50,
          width: 50,
        }}>stop</button>
      </div>
        <div>
          {frames.map((_, i) => <button style={{height: 50, width: 50, background: i==currFrame ? "#FF0000" : "#999999"}}
            id={"frame " + String(i)} onClick={loadFrame(i)}>{i}</button>)}
        </div>
    </div>
  );
}

export default App;
