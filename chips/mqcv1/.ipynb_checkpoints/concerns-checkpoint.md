Concerns: 

- Exact total length of coupling resonators: I used close fillets and anchors.
    - It's nearly exact but might be slightly off. Easy fix.
- Horizontal distance between flux line entry and exit terminations: 
    - Only the total distance matters. Easy fix.
- InlineIDC: Main GDS file has sharp edges—unsure if that's acceptable.
- Claws: I added fillets to the background, which don't exist in the main file.
- Component positioning: I did my best. 
    - Filleting with coupling resonators was tricky; 
    - I focused on keeping the resonators at the proper distance from the bus.
    - And how much resonator length is closest to the bus. 

- Flux line lengths: Based these on the distance between open-to-ground and input.
- Cheese buffers: Different chip parts use different values per the algorithm (like QNLDraw). 
    - I chose a default of 30 µm (the shortest no-cheese distance I found).
- InlineIDC cheeses: There are cheeses in the center even with a component present 
- Layering cheese: I haven't figured out how to put cheese on a different layer than main components.
- Alignment markers: There's no cheese buffer around them.
    - I don’t know how to differentiate no-cheese buffers for different components.
