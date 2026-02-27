import numpy as np
import cv2
import matplotlib.pyplot as plt
import os

def compute_histogram_stats(img):
    """
    Compute histogram, PDF, and CDF for grayscale or RGB image.

    Returns:
        hist : (256,) or (3,256)
        pdf  : same shape as hist
        cdf  : same shape as hist
    """

    # ==========================
    # Grayscale
    # ==========================
    if img.ndim == 2:
        hist = np.zeros(256, dtype=int)
        for v in img.flatten():
            hist[v] += 1

        pdf = hist / img.size
        cdf = pdf.cumsum()

        return hist, pdf, cdf

    # ==========================
    # RGB
    # ==========================
    elif img.ndim == 3:
        hist = np.zeros((3, 256), dtype=int)
        pdf = np.zeros((3, 256))
        cdf = np.zeros((3, 256))

        for c in range(3):
            for v in img[:, :, c].flatten():
                hist[c, v] += 1

            pdf[c] = hist[c] / img[:, :, c].size
            cdf[c] = pdf[c].cumsum()

        return hist, pdf, cdf
    


def draw_distribution(img, mode="hist", title="", save_path=None):
    """
    mode: 'hist', 'pdf', 'cdf'
    """

    hist, pdf, cdf = compute_histogram_stats(img)

    plt.figure(figsize=(8, 4))

    # ==========================
    # Grayscale
    # ==========================
    if img.ndim == 2:
        if mode == "hist":
            plt.bar(range(256), hist, color='gray', width=1)
            plt.ylabel("Frequency")

        elif mode == "pdf":
            plt.plot(range(256), pdf, color='black', linewidth=2)
            plt.ylabel("Probability")

        elif mode == "cdf":
            plt.plot(range(256), cdf, color='blue', linewidth=2)
            plt.ylabel("Cumulative Probability")

    # ==========================
    # RGB
    # ==========================
    else:
        colors = ['r', 'g', 'b']
        for c in range(3):
            if mode == "hist":
                plt.plot(range(256), hist[c], color=colors[c], label=colors[c].upper())
                plt.ylabel("Frequency")

            elif mode == "pdf":
                plt.plot(range(256), pdf[c], color=colors[c], label=colors[c].upper())
                plt.ylabel("Probability")

            elif mode == "cdf":
                plt.plot(range(256), cdf[c], color=colors[c], label=colors[c].upper())
                plt.ylabel("Cumulative Probability")

        plt.legend()

    plt.title(title)
    plt.xlabel("Pixel Value")
    plt.xlim([0, 255])
    plt.grid(alpha=0.3)

    if save_path:
        plt.savefig(save_path)

    plt.show()


def get_distribution_as_image(img, mode="hist", title="", figsize=(8, 4)):
    """
    Convert histogram/distribution to numpy image instead of displaying
    
    Args:
        img: Input image (grayscale or RGB)
        mode: 'hist', 'pdf', or 'cdf'
        title: Title for the plot
        figsize: Figure size (width, height)
        
    Returns:
        numpy array of the plot as an image
    """
    import matplotlib.pyplot as plt
    from io import BytesIO
    
    hist, pdf, cdf = compute_histogram_stats(img)
    
    fig = plt.figure(figsize=figsize)
    
    # ==========================
    # Grayscale
    # ==========================
    if img.ndim == 2:
        if mode == "hist":
            plt.bar(range(256), hist, color='gray', width=1)
            plt.ylabel("Frequency")
        elif mode == "pdf":
            plt.plot(range(256), pdf, color='black', linewidth=2)
            plt.ylabel("Probability")
        elif mode == "cdf":
            plt.plot(range(256), cdf, color='blue', linewidth=2)
            plt.ylabel("Cumulative Probability")
    
    # ==========================
    # RGB
    # ==========================
    else:
        colors = ['r', 'g', 'b']
        for c in range(3):
            if mode == "hist":
                plt.plot(range(256), hist[c], color=colors[c], label=colors[c].upper())
                plt.ylabel("Frequency")
            elif mode == "pdf":
                plt.plot(range(256), pdf[c], color=colors[c], label=colors[c].upper())
                plt.ylabel("Probability")
            elif mode == "cdf":
                plt.plot(range(256), cdf[c], color=colors[c], label=colors[c].upper())
                plt.ylabel("Cumulative Probability")
        
        plt.legend()
    
    plt.title(title)
    plt.xlabel("Pixel Value")
    plt.xlim([0, 255])
    plt.grid(alpha=0.3)
    
    # Convert plot to numpy array
    buf = BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight', dpi=100)
    buf.seek(0)
    
    # Read as image
    from PIL import Image
    img_pil = Image.open(buf)
    plot_image = np.array(img_pil)
    
    plt.close(fig)
    buf.close()
    
    # Convert RGBA to RGB if needed
    if plot_image.shape[2] == 4:
        plot_image = cv2.cvtColor(plot_image, cv2.COLOR_RGBA2BGR)
    else:
        plot_image = cv2.cvtColor(plot_image, cv2.COLOR_RGB2BGR)
    
    return plot_image



def histogram_equalization(img, save_name=None):
    """
    Histogram Equalization for grayscale or RGB image
    """

    def equalize_gray(gray):
        hist, _, cdf = compute_histogram_stats(gray)
        cdf_min = cdf[cdf > 0].min()
        n = gray.size

        if n == cdf_min:
            return gray.copy()

        eq = np.round((cdf[gray] - cdf_min) / (1 - cdf_min) * 255)
        return eq.astype(np.uint8)

    # ==========================
    # Grayscale
    # ==========================
    if img.ndim == 2:
        result = equalize_gray(img)

    # ==========================
    # RGB (equalize luminance only)
    # ==========================
    else:
        img_ycc = cv2.cvtColor(img, cv2.COLOR_RGB2YCrCb)
        img_ycc[:, :, 0] = equalize_gray(img_ycc[:, :, 0])
        result = cv2.cvtColor(img_ycc, cv2.COLOR_YCrCb2RGB)

    if save_name:
        os.makedirs("equalized", exist_ok=True)
        np.save(os.path.join("equalized", save_name), result)

    return result
