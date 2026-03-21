import time
import math
from PIL import Image

WIDTH = 100 

def get_frame(img_data, is_talking=False, idle_time=0, is_smiling=False):
    chars = "@#%*+      "
    t = time.time()
    
    speed = 0.16 if is_talking else 0.05
    sway_y = math.cos(t * (speed * 0.9)) * (1.2 if is_talking else 0.5)
    
    side_sway = 0
    if not is_talking and idle_time > 5:
        side_sway = math.sin((t - 5) * 0.4) * 3.0 
    
    sway_x = (math.sin(t * speed) * (2.0 if is_talking else 0.8)) + side_sway
    
    w, h = img_data.size
    new_width = WIDTH
    new_height = int((h / w) * new_width * 0.36)
    
    m_y_c = int(new_height * 0.60)
    e_y_c = int(new_height * 0.36) 
    e_l_x, e_r_x = int(new_width * 0.18), int(new_width * 0.50) 
    e_w = int(new_width * 0.15) 

    mouth_open = math.sqrt(abs(math.sin(t * 8.5))) if is_talking else 0.05
    eye_open = 0.6 + 0.3 * math.sin(t * 1.1)
    
    look_x = (math.sin(t * 0.85)) + (side_sway * 0.2)
    look_y = math.cos(t * 0.45) * 0.3

    ascii_frame = []
    for y in range(new_height):
        line = ""
        pivot_inf = math.pow(max(0, min(1, (y - (new_height * 0.98)) / -(new_height * 0.85))), 2.0)

        for x in range(new_width):
            dx = abs(x - new_width/2) / (new_width/2)
            dy = abs(y - new_height/2) / (new_height/2)
            mask = max(0, 1.2 - (dx**1.5 + dy**1.5))
            mask = min(1.0, mask) 
            total_inf = pivot_inf * mask

            target_x = x + (sway_x * total_inf)
            target_y = y - (sway_y * total_inf)
            
            orig_x = max(0, min(w - 1, int((target_x / new_width) * w)))
            orig_y = max(0, min(h - 1, int((target_y / new_height) * h)))
            
            sample_y = orig_y
            is_void = False
            char_override = None

            if mask > 0.05:
                # --- EYES ---
                if (e_l_x < x < e_l_x + e_w) or (e_r_x < x < e_r_x + e_w):
                    ex_s = e_l_x if x < e_r_x else e_r_x
                    e_h = abs((x - (ex_s + e_w/2)) / (e_w/2))
                    e_t = math.pow(math.cos(e_h * (math.pi / 2)), 1.2)
                    e_range = (new_height * 0.05) * e_t
                    dist_e = abs(y - e_y_c)
                    if dist_e < e_range:
                        strength = (e_range - dist_e) / e_range
                        s_eye = 0.4 if is_smiling else 1.0
                        e_shift = (-1 if y < e_y_c else 1) * eye_open * 4.5 * strength * e_t * s_eye
                        sample_y = max(0, min(h - 1, int(orig_y + e_shift)))
                        if eye_open > 0.1 and dist_e < (e_range * eye_open * 0.85):
                            is_void = True
                            p_x = (ex_s + e_w/2) + (look_x * 1.5)
                            p_y = e_y_c + (look_y * 0.5)
                            dist_p = math.sqrt((y - p_y)**2 + (x - p_x)**2)
                            if dist_p < 1.1: char_override = "█" 
                            elif dist_p < 2.0: char_override = "O" 

                # --- MOUTH (Larger horizontally for Male) ---
                if not char_override and (new_width*0.22 < x < new_width*0.58):
                    m_h = abs((x - (new_width*0.4)) / (new_width*0.18))
                    m_t = math.cos(max(-1.5, min(1.5, m_h * (math.pi / 2))))
                    m_range = (new_height * 0.06) * m_t
                    
                    smile_pull = (m_h**2) * 2.5 if is_smiling else 0
                    
                    dist_m = abs(y - (m_y_c - smile_pull))
                    if dist_m < m_range:
                        m_str = (m_range - dist_m) / m_range
                        m_s = (-1 if y < m_y_c else 1) * mouth_open * 7.5 * m_str * m_t
                        sample_y = max(0, min(h - 1, int(orig_y + m_s)))
                        if mouth_open > 0.3 and dist_m < (m_range * mouth_open * 0.6):
                            is_void = True

            if char_override: line += char_override
            elif is_void: line += " "
            else:
                pixel = img_data.getpixel((orig_x, max(0, min(h-1, int(sample_y)))))
                val = pixel[0] if isinstance(pixel, tuple) else pixel
                line += chars[min(val // 26, 9)]
        ascii_frame.append(line)
    
    while len(ascii_frame) > 1 and ascii_frame[0].strip() == "": ascii_frame.pop(0)
    while len(ascii_frame) > 1 and ascii_frame[-1].strip() == "": ascii_frame.pop()

    return "\n".join(ascii_frame)