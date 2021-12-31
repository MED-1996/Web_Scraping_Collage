# Import python modules.

from PIL import Image
import requests
import bs4
import os

# Custom exception for non-wikipedia URL's

class NotWikipediaException(Exception):
    def __init__(self, message='Not a wikipedia URL.'):
        super().__init__(message)

# Function to obtain a valid wikipedia URL from the user. Returns the request.

def enterWikipedia():
    
    valid_url = False
    res = 0

    while not valid_url:

        try:
            website_url = input('Please enter a Wikipedia URL you\'d like to scrape: ')

            if 'wikipedia.org' not in website_url:
                raise NotWikipediaException()

            else:
                res = requests.get(website_url)

        except requests.exceptions.MissingSchema:
            print(f'\'{website_url}\' - Invalid URL: Incorrect URL format.')

        except NotWikipediaException:
            print(f'\'{website_url}\' - Invalid URL: Not a Wikipedia URL.')

        except requests.exceptions.ConnectionError:
            print(f'\'{website_url}\' - Invalid URL: Unable to connect to the given URL')

        except:
            print(f'\'{website_url}\' - Invalid URL')

        else:
            print(f'\'{website_url}\' - Valid URL!')
            valid_url = True
    
    return res

# Function that saves all images to the current working directory. Takes in a list of images.
# Returns how many images were downloaded.

def numImages(images: list) -> int:
    
    img_success = 0
    img_fail = 0

    for image in images:

        try:
            image_src = image['src']
            image_url = f'https:{image_src}'
            image_response = requests.get(image_url)
            file = open(f'Image_{img_success}.png', 'wb')
            file.write(image_response.content)
            file.close()
            img_success += 1

        except:
            img_fail += 1

    print('***{Download Complete}***')
    print(f'Successful Image Downloads: {img_success} of {len(images)}')
    print(f'Failed Image Downloads: {img_fail} of {len(images)}')
    
    return img_success

# Takes in the total size of the collage (square shape), in pixels,
# & the number of images that will be inside the collage.
# Returns the number of columns the collage will have,
# along with the image size of each image in pixels (square shape).

def collageDimension(collage_size: int, num_images: int) -> (int, int):
    
    num_columns = -(-(num_images ** 0.5) // 1)
    
    img_size = collage_size / num_columns
    
    return (int(num_columns), int(img_size))



# Portion of the script where the user interaction logic is written. {Main function}
#_*_*_*_*_*_*_*_*_*_*_*_*_*_*_*_*_*_*_*_*_*_*_*_*_*_*_*_*_*_*_*_*_*_*_*_*_*_*_*_*_*_#

# Step 1: Ask the user to enter the collage size they'd like.

def main():

    collage_size = 0

    while True:
        
        try:
            collage_size = int(input('Enter the pixel size of your square collage [100px, 2000px]: '))
            
            # The collage should be no less than a 100px x 100px & no greater than a 2000px x 2000px .png
            if (collage_size < 100) or (collage_size > 2000):
                print('ERROR: please enter an integer between 100 & 2000.')
                continue
                
            else:
                break
                
        except:
            print('ERROR: please enter an integer between 100 & 2000.')

    # Step 2: Ask the user to enter a wikipedia website.

    res = enterWikipedia()

    # Step 3: Extract images from the wikipedia page & download them to the current working directory.

    print('\n...{Downloading Images}...\n')
    soup = bs4.BeautifulSoup(res.text, 'lxml')
    images = soup.select('img')
    number_of_images = numImages(images)

    # Step 4: If no images were downloaded, then a collage can't be created. The script ends here. 

    if number_of_images <= 0:
        print('ERROR: 0 images downloaded, cannot make a collage with 0 images.')
        print('Please try a different wikipedia URL!')

    # Step 5: If at least 1 image was downloaded we will begin making a collage.

    else:
        (number_of_columns, image_size) = collageDimension(collage_size, number_of_images)
        
        # Import the white collage background & resize it to the collage dimension.
        background = Image.open('Collage_Background.png')
        background = background.resize((collage_size, collage_size))
        
        # Starting in the top-left corner of the background, begin pasting images onto the background.
        x_posistion = 0
        y_posistion = 0
        
        # Goes through all the downloaded images & paste them to the background.
        for num in range(0, number_of_images):
            image_file_name = f'Image_{num}.png'
            current_image = Image.open(image_file_name)
            current_image = current_image.resize((image_size,image_size))
            background.paste(im=current_image,box=(x_posistion,y_posistion))
            
            # If we are at the end of a row, reset the coordinates for the next image in the next row.
            if (num+1) % number_of_columns == 0:
                x_posistion = 0
                y_posistion += image_size
                
            else:
                x_posistion += image_size
            
            # removes the image from folder as it is no longer needed
            os.remove(image_file_name)
        
        # collage is added to the folder and named the title of the wikipedia article.
        title = soup.select('h1')[0].getText()
        background.save(f'{title}.png')
        print(f'\n\'{title}.png\' has been created and saved.')

if __name__ == "__main__":
    main()