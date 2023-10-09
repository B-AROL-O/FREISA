import os
import sys

from heic2png import HEIC2PNG

if __name__ == "__main__":
    # Argv[1]: input image path or folder of images
    # Argv[2] (optional): output path (needs to be a folder if the input is a folder as well)

    if len(sys.argv) <= 1:
        raise ValueError("Missing input file(s)!")

    in_path = str(sys.argv[1])
    if os.path.exists(in_path):
        if os.path.isfile(in_path):
            # Single image was specified
            if in_path.split(".")[-1] == "heic":
                out_img = HEIC2PNG(in_path)
                try:
                    out_img.save(str(sys.argv[2]))
                    print("Image was converted!")
                except:
                    print("Converted image stored in original folder")
                    out_img.save()
                else:
                    pass
            else:
                raise ValueError("Image is not in '.heic' format!")
        elif os.path.isdir(in_path):
            # Entire folder was specified
            flg = False
            if len(sys.argv) > 2:
                assert os.path.isdir(
                    sys.argv[2]
                ), "The output path needs to be a folder as well!"
                flg = True
            n_conv = 0
            for f in os.listdir(in_path):
                if f.split(".")[-1] == "heic":
                    out_img = HEIC2PNG(os.path.join(in_path, f))
                    if flg:
                        img_name = f.split(".")[:-1]
                        out_png = ".".join(img_name + ["png"])
                        out_img.save(os.path.join(sys.argv[2], out_png))
                        n_conv += 1
                    else:
                        out_img.save()
                        n_conv += 1
            print(f"{n_conv} images have been converted")
            if not flg:
                print("Converted images have been stored in the original folder")
    else:
        raise ValueError("Invalid path for source image(s)")
