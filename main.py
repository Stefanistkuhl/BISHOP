import pandas as pd
from PIL import Image, ImageDraw, ImageOps
import praw
from datetime import datetime, timedelta 
import math
import os
from imgurpython import ImgurClient
import time
anz_bishops = 65536
counter = 0
total_bishops_posted = 0

 #reddit account setup
reddit = praw.Reddit(client_id='no',
    client_secret='no',
    username='Bishoplover69',
    password='no',
    user_agent='BishopMosaicApp/0.0.1 (by u/Bishoplover69)')
print(reddit.user.me())
#imgur acc
imgur_client_id = 'no'
imgur_client_secret = 'no'

while True:
   
    #imgur bild upload
    if counter == 0:
        cwd = os.getcwd()
        imgur_client = ImgurClient(imgur_client_id, imgur_client_secret)
        blank_image_path = os.path.join(cwd, "leer.png")
        blank_uploaded_image = imgur_client.upload_from_path(blank_image_path, config=None, anon=True)

        blank_image_url = blank_uploaded_image['link']


        #reddit post
        #funktion für likes geben schreiben
        subreddit_name = "AnarchyChess"

        #posttietel rein machen
        post_title = "Day 1 of of The Chess Bishop Bishop-athon! Your upvotes determine how many bishops fit inside!"
        datum_post = datetime.now.strftime("%Y-%m-%d %H:%M:%S")
        day_after_post = datum_post + timedelta(hours=24)
        day_after_post = day_after_post.strftime("%Y-%m-%d %H:%M:%S")

        subreddit = reddit.subreddit(subreddit_name)
        post = subreddit.submit(post_title, url=blank_image_url)
        post.refresh
        likes = post.score()
    
    cwd = os.getcwd()
    file_name = counter + ".png"
    imgur_client = ImgurClient(imgur_client_id, imgur_client_secret)
    image_path = os.path.join(cwd, file_name)
    uploaded_image = imgur_client.upload_from_path(image_path, config=None, anon=True)

    image_url = uploaded_image['link']


    #reddit post
    #funktion für likes geben schreiben
    subreddit_name = "AnarchyChess"

    #posttietel rein machen
    post_title = "Day" + counter + "of The Chess Bishop Bishop-athon! Your upvotes determine how many bishops fit inside!"
    datum_post = datetime.now.strftime("%Y-%m-%d %H:%M:%S")
    day_after_post = datum_post + timedelta(hours=24)
    day_after_post = day_after_post.strftime("%Y-%m-%d %H:%M:%S")

    subreddit = reddit.subreddit(subreddit_name)
    post = subreddit.submit(post_title, url=image_url)
    post.refresh()
    likes = post.score()

    cwd = os.getcwd()
    csv_file = os.path.join(cwd, "aja.csv")
    #csv magic
    if os.path.isfile(csv_file):
        df = pd.read_csv(csv_file)
    else:
        df = pd.DataFrame()

    likes_sum = int(df['likes'].sum()) if 'likes' in df.columns else 0
    likes_added = likes + int(likes_sum)

    new_row = pd.DataFrame({'post_date': [datum_post], 'post_title': [post_title], 'likes': [likes], 'likes_added': [likes_added]})
    df = pd.concat([df, new_row], ignore_index=True)


    df.to_csv(csv_file, index=False)
    #imagetest

    images_to_add = likes
    images_to_process = min(anz_bishops, likes_sum + images_to_add)

    img_bishop = Image.open("BISHOP.png")
    canvas = Image.new('RGB', (8192,8192))
    target = Image.open("Bishop_full.png")

    canvas_size = 8192
    b_size = 512

    num_cols = int(math.ceil(math.sqrt(anz_bishops)))
    num_rows = int(math.ceil(anz_bishops / num_cols))

    b_size = min(canvas_size // num_cols, canvas_size // num_rows)
    spacing = (canvas_size - b_size * num_cols) // (num_cols + 1)


    #target image to grid
    cell_width = canvas_size // num_cols
    cell_height = canvas_size // num_rows

    grid = [[0] * num_cols for _ in range(num_rows)]
    id_counter = 1
    for row in range(num_rows):
        for col in range(num_cols):
            grid[row][col] = id_counter
            id_counter += 1

    def get_average_color(image, row, col, cell_width, cell_height):
        x1 = col*cell_width
        y1 = row*cell_height
        x2 = x1+cell_width
        y2 = y1 + cell_height

        r_total, g_total, b_total = 0,0,0
        pixel_count = 0
        for x in range (x1,x2):
            for y in range (y1,y2):
                r,g,b = image.getpixel((x,y))
                r_total += r
                g_total += g
                b_total += b
                pixel_count += 1
        
        r_avg = r_total // pixel_count
        g_avg = g_total // pixel_count
        b_avg = b_total // pixel_count

        return r_avg, g_avg, b_avg
    def colorize_image(image, target_color):
        grayscale_img = ImageOps.grayscale(image)

        colored_img = ImageOps.colorize(grayscale_img, 'black', target_color)
        return colored_img


    # Step 5: Replace grid cells with small images
    for row in range(num_rows):
        for col in range(num_cols):
            img_index = row * num_cols + col
            if img_index < images_to_process:
                # Resize and paste image
                
                average_color = get_average_color(target, row, col, cell_width, cell_height)
                    
                colored_img_bishop = colorize_image(img_bishop, average_color)

                resized_colored_img_bishop = colored_img_bishop.resize((b_size, b_size), resample=Image.LANCZOS)
                x = spacing + col * (b_size + spacing)
                y = spacing + row * (b_size + spacing)
                canvas.paste(resized_colored_img_bishop, (x, y))
    # Step 6: Merge the small images
    draw = ImageDraw.Draw(canvas)

    canvas.save(file_name)
    total_bishops_posted += likes
    counter += 1
    if total_bishops_posted < anz_bishops:
        time.sleep(24 * 60 * 60)
    if total_bishops_posted >= anz_bishops:
        break
    