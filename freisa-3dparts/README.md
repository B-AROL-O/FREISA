# FREISA 3D-Printable Parts

| Folder              | Description                           |
| ------------------- | ------------------------------------- |
| [`STL`](STL/)       | Mesh (files suitable for 3D-printing) |
| [`STP`](STP/)       | 3D Model (STEP)                       |
| [`images`](images/) | 3D rendering of parts and assemblies  |

## Pupper Head for FREISA v3.0 (2025)

[Eric](http://github.com/OrsoEric) wanted to make a dog-shaped LEGO&reg;-compatible RaspiCAM Holder for the Mini Pupper 2.

1. He used ComfyUI with Flux model to create a base image and Hunyuan3D model to convert the image to an STL with my [ComfyUI workflow](https://github.com/OrsoEric/HOWTO-ComfyUI#img-to-stl---3d-workflow-hunyuan) running locally on my 7900XTX

![2025-09-06-T1022-Pupper-Head-Creality.png](images/2025-09-06-T1022-Pupper-Head-Creality.png)

2. He used Creality Studio to cut and combine the dog head model with the OpenSCAD LEGO plate I developed for the previous hackaton and the Screwless Raspicam Holder I made in OpenSCAD

![2025-09-07-T1113%20Pupper%20Head%20Assembly.png](images/2025-09-07-T1113%20Pupper%20Head%20Assembly.png)

3. He sliced and printed the head with my Creality K1, first attempt was good

4. He installed the head on my red pupper and connected the raspicam. It does look like a muffler.

![2025-09-07-T1259%20Pupper%20Head.jpg](images/2025-09-07-T1259%20Pupper%20Head.jpg)

Links to 3D-printable parts:

- [Pupper Head STL](STL/Pupper_Head_Hunyuan3D.stl)
- [Pupper Head LEGO&reg; Plate STL](STL/LEGO-4x5.stl)

## FREISA v1.0 3D Parts (2023)

Developed and contributed by [Gianfranco Poncini](https://github.com/@Muwattalli).

Links to 3D-printable parts:

- [Biella.STL](STL/Biella.STL)
- [Body_Back_supporti.STL](STL/Body_Back_supporti.STL)
- [Body_Back_supporti_low.STL](STL/Body_Back_supporti_low.STL)
- [Holder.STL](STL/Holder.STL)
- [Leva.STL](STL/Leva.STL)
- [Pusher.STL](STL/Pusher.STL)
- [Rocco.STL](STL/Rocco.STL)
- [Shell_battery_up_Barolo.STL](STL/Shell_battery_up_Barolo.STL)
- [Tank.STL](STL/Tank.STL)
- [Tappo.STL](STL/Tappo.STL)

### Rendering of FREISA 3D-Parts Assembly

Rendering performed with [Salome-Meca 2023](https://code-aster-windows.com/category/posts/salome_meca-windows/)

![Freisa_1.jpg](images/Freisa_1.jpg)

![Freisa_2.jpg](images/Freisa_2.jpg)

![Freisa_3.jpg](images/Freisa_3.jpg)

![Freisa_4.jpg](images/Freisa_4.jpg)

### Rendering of FREISA 3D-Parts attached to Mini Pupper

Rendering performed with [Salome-Meca 2023](https://code-aster-windows.com/categor

![Full_1.jpg](images/Full_1.jpg)

![Full_2.jpg](images/Full_2.jpg)

![Full_3.jpg](images/Full_3.jpg)

![Full_4.jpg](images/Full_4.jpg)

![Full_5.jpg](images/Full_5.jpg)

![Full_6.jpg](images/Full_6.jpg)

## See also

- [OpenSCAD-lego-library](https://github.com/B-AROL-O/OpenSCAD-lego-library): OpenSCAD library to draw LEGO&reg; beams and LEGO plates with custom patterns

<!-- EOF -->
