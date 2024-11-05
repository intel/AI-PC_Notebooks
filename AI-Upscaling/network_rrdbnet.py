# Sourced from https://github.com/cszn/BSRGAN/blob/main/models/network_rrdbnet.py

import functools

import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.nn.init as init


def initialize_weights(net_l, scale=1):
    """initialization of network weights

    Args:
        net_l (list): list of layers
        scale (int, optional): scaling factor. Defaults to 1.
    """
    try:
        if not isinstance(net_l, list):
            net_l = [net_l]
        for net in net_l:
            for m in net.modules():
                if isinstance(m, nn.Conv2d):
                    init.kaiming_normal_(m.weight, a=0, mode="fan_in")
                    m.weight.data *= scale  # for residual block
                    if m.bias is not None:
                        m.bias.data.zero_()
                elif isinstance(m, nn.Linear):
                    init.kaiming_normal_(m.weight, a=0, mode="fan_in")
                    m.weight.data *= scale
                    if m.bias is not None:
                        m.bias.data.zero_()
                elif isinstance(m, nn.BatchNorm2d):
                    init.constant_(m.weight, 1)
                    init.constant_(m.bias.data, 0.0)
    except Exception as e:
        print("Error initializing weights")
        raise e


def make_layer(block, n_layers):
    """make layer by stacking the same block

    Args:
        block (callable): block to stack
        n_layers (int): number of layers to stack

    Returns:
        nn.Sequential: stacked layers
    """
    try:
        layers = []
        for _ in range(n_layers):
            layers.append(block())
        return nn.Sequential(*layers)
    except Exception as e:
        print("Error making layer")
        raise e


class ResidualDenseBlock_5C(nn.Module):
    """Residual Dense Block

    Args:
        nn (Module): PyTorch module
    """

    def __init__(self, nf=64, gc=32, bias=True):
        """Initialization

        Args:
            nf (int, optional): number of filters. Defaults to 64.
            gc (int, optional): growth channel. Defaults to 32.
            bias (bool, optional): bias. Defaults to True.
        """
        try:
            super(ResidualDenseBlock_5C, self).__init__()
            # gc: growth channel, i.e. intermediate channels
            self.conv1 = nn.Conv2d(nf, gc, 3, 1, 1, bias=bias)
            self.conv2 = nn.Conv2d(nf + gc, gc, 3, 1, 1, bias=bias)
            self.conv3 = nn.Conv2d(nf + 2 * gc, gc, 3, 1, 1, bias=bias)
            self.conv4 = nn.Conv2d(nf + 3 * gc, gc, 3, 1, 1, bias=bias)
            self.conv5 = nn.Conv2d(nf + 4 * gc, nf, 3, 1, 1, bias=bias)
            self.lrelu = nn.LeakyReLU(negative_slope=0.2, inplace=True)

            # initialization
            initialize_weights(
                [self.conv1, self.conv2, self.conv3, self.conv4, self.conv5], 0.1
            )
        except Exception as e:
            print("Error initializing ResidualDenseBlock_5C")
            raise e

    def forward(self, x):
        """forward pass

        Args:
            x (torch.Tensor): input tensor

        Returns:
            torch.Tensor: output tensor
        """
        try:
            x1 = self.lrelu(self.conv1(x))
            x2 = self.lrelu(self.conv2(torch.cat((x, x1), 1)))
            x3 = self.lrelu(self.conv3(torch.cat((x, x1, x2), 1)))
            x4 = self.lrelu(self.conv4(torch.cat((x, x1, x2, x3), 1)))
            x5 = self.conv5(torch.cat((x, x1, x2, x3, x4), 1))
            return x5 * 0.2 + x
        except Exception as e:
            print("Error in ResidualDenseBlock_5C forward pass")
            raise e


class RRDB(nn.Module):
    """Residual in Residual Dense Block

    Args:
        nn (Module): PyTorch module
    """

    def __init__(self, nf, gc=32):
        """Initialization

        Args:
            nf (int): number of filters
            gc (int, optional): growth channel. Defaults to 32.
        """
        try:
            super(RRDB, self).__init__()
            self.RDB1 = ResidualDenseBlock_5C(nf, gc)
            self.RDB2 = ResidualDenseBlock_5C(nf, gc)
            self.RDB3 = ResidualDenseBlock_5C(nf, gc)
        except Exception as e:
            print("Error initializing RRDB")
            raise e

    def forward(self, x):
        """forward pass

        Args:
            x (torch.Tensor): input tensor

        Returns:
            torch.Tensor: output tensor
        """
        try:
            out = self.RDB1(x)
            out = self.RDB2(out)
            out = self.RDB3(out)
            return out * 0.2 + x
        except Exception as e:
            print("Error in RRDB forward pass")
            raise e


class RRDBNet(nn.Module):
    """RRDBNet architecture

    Args:
        nn (Module): PyTorch module
    """

    def __init__(self, in_nc=3, out_nc=3, nf=64, nb=23, gc=32, sf=4):
        """Initialization

        Args:
            in_nc (int, optional): Number of input channels. Defaults to 3.
            out_nc (int, optional): Number of output channels. Defaults to 3.
            nf (int, optional): Number of filters. Defaults to 64.
            nb (int, optional): Number of blocks. Defaults to 23.
            gc (int, optional): Growth channel. Defaults to 32.
            sf (int, optional): Scale factor. Defaults to 4.
        """
        try:
            super(RRDBNet, self).__init__()
            RRDB_block_f = functools.partial(RRDB, nf=nf, gc=gc)
            self.sf = sf

            self.conv_first = nn.Conv2d(in_nc, nf, 3, 1, 1, bias=True)
            self.RRDB_trunk = make_layer(RRDB_block_f, nb)
            self.trunk_conv = nn.Conv2d(nf, nf, 3, 1, 1, bias=True)
            # upsampling
            self.upconv1 = nn.Conv2d(nf, nf, 3, 1, 1, bias=True)
            if self.sf == 4:
                self.upconv2 = nn.Conv2d(nf, nf, 3, 1, 1, bias=True)
            self.HRconv = nn.Conv2d(nf, nf, 3, 1, 1, bias=True)
            self.conv_last = nn.Conv2d(nf, out_nc, 3, 1, 1, bias=True)

            self.lrelu = nn.LeakyReLU(negative_slope=0.2, inplace=True)
        except Exception as e:
            print("Error initializing RRDBNet")
            raise e

    def forward(self, x):
        """forward pass

        Args:
            x (torch.Tensor): input tensor

        Returns:
            torch.Tensor: output tensor
        """
        try:
            fea = self.conv_first(x)
            trunk = self.trunk_conv(self.RRDB_trunk(fea))
            fea = fea + trunk

            up_size_1 = (fea.size(2) * 2, fea.size(3) * 2)
            fea = self.lrelu(
                self.upconv1(F.interpolate(fea, size=up_size_1, mode="nearest"))
            )

            if self.sf == 4:
                up_size_2 = (fea.size(2) * 2, fea.size(3) * 2)
                fea = self.lrelu(
                    self.upconv2(F.interpolate(fea, size=up_size_2, mode="nearest"))
                )

            out = self.conv_last(self.lrelu(self.HRconv(fea)))

            return out
        except Exception as e:
            print("Error in RRDBNet forward pass")
            raise e
