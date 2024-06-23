import React, { useEffect, useState } from "react";
import { formatExpression } from "./format";

type Props = {
  targetImage: File | null;
  setTargetImage: React.Dispatch<React.SetStateAction<File | null>>;
};

const expressions = [
  "(Div(Style(Junctborder:2pxgreenwidth:100px))(Compose(Div(Style(Junct(Junctwidth:24px(Junctmargin-top:auto(Junct(Junctmargin-left:B%(Junctwidth:24px(Junct(Junctborder:8pxredmargin-left:3px)(Junctwidth:2pxwidth:50%))))(Junctwidth:2pxmargin-left:2px))))(Junctmargin-right:24%(Junctborder:100%redmargin-left:auto))))(P'12'))(Compose(Div(Stylemargin-left:36px)(P'F'))(Compose(Compose(Div(Style(Junctborder:2pxblue(Junctborder:50%green(Junctmargin-left:automargin-right:auto))))(Compose(P'100')(Compose(P'100')(P'100'))))(Div(Style(Junctwidth:24%(Junctmargin-right:8pxmargin-left:7px)))(P'8')))(Div(Style(Junctborder:2pxred(Junctmargin-top:50pxwidth:100%)))(Div(Style(Junctwidth:24%(Junctheight:24px(Junctmargin-left:automargin-right:auto))))(P'12')))))))",
  "(Div(Style(Junctborder:2pxgreenwidth:100%))(Compose(Div(Style(Junct(Junctwidth:24px(Junctmargin-top:auto(Junct(Junctmargin-left:B%(Junctwidth:24px(Junct(Junctborder:8pxredmargin-left:3px)(Junctwidth:2pxwidth:50%))))(Junctwidth:2pxmargin-left:2px))))(Junctmargin-right:24%(Junctborder:50%redmargin-left:auto))))(P'12'))(Compose(Div(Stylemargin-left:36px)(P'F'))(Compose(Compose(P'100')(Div(Style(Junctwidth:24%(Junctmargin-right:8pxmargin-left:7px)))(P'8')))(Div(Style(Junctborder:2%red(Junctmargin-top:50pxwidth:100%)))(Div(Style(Junctwidth:24%(Junctheight:24px(Junctmargin-left:automargin-right:auto))))(P'12')))))))",
  "(Div(Style(Junctborder:2pxgreenwidth:100%))(Compose(Div(Style(Junct(Junctwidth:24px(Junctmargin-top:auto(Junct(Junctmargin-left:B%(Junctwidth:24px(Junct(Junctborder:8pxredmargin-left:3px)(Junctwidth:2pxwidth:50%))))(Junctwidth:2pxmargin-left:2px))))(Junctmargin-right:24%(Junctborder:50%redmargin-left:auto))))(P'12'))(Compose(Div(Stylemargin-left:36px)(P'F'))(Compose(Compose(P'100')(Div(Style(Junctwidth:24%(Junctmargin-right:8pxmargin-left:7px)))(P'8')))(Div(Style(Junctborder:2pxred(Junctmargin-top:50pxwidth:100%)))(Div(Style(Junctwidth:24%(Junctheight:24px(Junctmargin-left:automargin-right:auto))))(P'12')))))))",
  "(Div(Style(Junctborder:24%bluewidth:2px))(Compose(Div(Style(Junctborder:3pxbluewidth:5%))(P'36'))(Compose(Div(Stylewidth:24%)(P'F'))(Compose(Compose(Div(Style(Junctmargin-top:50px(Junctwidth:50%(Junctmargin-left:8pxmargin-right:auto))))(Compose(P'100')(Compose(P'100')(P'100'))))(Div(Style(Junctwidth:24%(Junctmargin-right:8pxmargin-left:auto)))(P'8')))(Div(Style(Junctborder:2pxred(Junctmargin-top:50pxmargin-right:100%)))(Div(Style(Junctwidth:24%(Junctheight:24px(Junctmargin-left:A%margin-right:auto))))(P'12')))))))",
  "(Div(Style(Junctborder:24%bluewidth:2px))(Compose(Div(Style(Junctborder:3pxbluewidth:5%))(P'36'))(Compose(Div(Stylewidth:24%)(P'F'))(Compose(Compose(Div(Style(Junctmargin-top:50px(Junctmargin-right:autoheight:8px)))(Compose(P'100')(Compose(P'100')(P'100'))))(Div(Style(Junctwidth:24%(Junctmargin-right:8pxmargin-left:auto)))(P'8')))(Div(Style(Junctborder:2pxred(Junctmargin-top:50pxmargin-right:100%)))(Div(Style(Junctwidth:24%(Junctheight:24px(Junctmargin-left:A%margin-right:auto))))(P'12')))))))",
  "(Div(Style(Junctborder:24%bluewidth:2px))(Compose(Div(Style(Junctborder:3pxbluewidth:5%))(P'36'))(Compose(Div(Stylewidth:24%)(P'F'))(Compose(Compose(Div(Style(Junctmargin-top:50px(Junctwidth:50%(Junctmargin-left:8pxmargin-right:auto))))(Compose(P'100')(Compose(P'100')(Compose(P'12')(Compose(P'100')(P'100'))))))(Div(Style(Junctwidth:24%(Junctmargin-right:8pxmargin-left:auto)))(P'8')))(Div(Style(Junctborder:2pxred(Junctmargin-top:50pxmargin-right:100%)))(Div(Style(Junctwidth:24%(Junctheight:24px(Junctmargin-left:A%margin-right:auto))))(P'12')))))))",
  "(Div(Style(Junctborder:24pxbluewidth:2px))(Compose(Div(Style(Junctborder:3pxbluewidth:5%))(P'36'))(Compose(Div(Stylewidth:24%)(P'F'))(Compose(Compose(Div(Style(Junctmargin-right:100%(Junctwidth:50%(Junctmargin-left:8pxmargin-right:auto))))(Compose(P'100')(Compose(P'100')(Compose(P'12')(Compose(P'100')(P'100'))))))(Div(Style(Junctwidth:24%(Junctmargin-right:8pxmargin-left:auto)))(P'8')))(Div(Style(Junctborder:2pxred(Junctmargin-top:50pxmargin-right:100%)))(Div(Style(Junctwidth:24%(Junctheight:24px(Junctmargin-left:A%margin-right:auto))))(P'12')))))))",
  "(Div(Style(Junctborder:24pxbluewidth:2px))(Compose(Div(Style(Junctborder:3pxbluewidth:5%))(P'36'))(Compose(Div(Stylewidth:24%)(P'F'))(Compose(Compose(Div(Style(Junctborder:2pxblue(Junctwidth:50%(Junctmargin-left:8pxmargin-right:auto))))(Compose(P'100')(Compose(P'100')(Compose(P'12')(Compose(P'100')(P'100'))))))(Div(Style(Junctwidth:24%(Junctmargin-right:8pxmargin-left:auto)))(P'8')))(Div(Style(Junctborder:2pxred(Junctmargin-top:50pxmargin-right:100%)))(Div(Style(Junctwidth:24%(Junctheight:24px(Junctmargin-left:A%margin-right:auto))))(P'12')))))))",
  "(Div(Style(Junctborder:2%greenwidth:2px))(Compose(Div(Style(Junctborder:3pxbluewidth:5%))(P'12'))(Compose(Div(Styleheight:50%)(P'F'))(Compose(Compose(Div(Style(Junctborder:2pxblue(Junctwidth:50%(Junctmargin-left:8pxmargin-right:auto))))(Compose(P'100')(Compose(P'100')(Compose(P'100')(Compose(P'100')(P'100'))))))(Div(Style(Junctwidth:24%(Junctmargin-right:8pxmargin-left:auto)))(P'8')))(Div(Style(Junctborder:2pxred(Junctmargin-top:50pxwidth:100%)))(Div(Style(Junctwidth:24%(Junctheight:24px(Junctmargin-left:automargin-right:auto))))(P'12')))))))",
  "(Div(Style(Junctborder:2%greenwidth:2px))(Compose(Div(Style(Junctborder:3pxbluewidth:5%))(P'12'))(Compose(Div(Stylemargin-left:36px)(P'F'))(Compose(Compose(Div(Style(Junctborder:2pxblue(Junctwidth:50%(Junctmargin-left:8pxmargin-right:auto))))(Compose(P'100')(Compose(P'100')(Compose(P'100')(Compose(P'100')(P'100'))))))(Div(Style(Junctwidth:24%(Junctmargin-right:8pxmargin-left:auto)))(P'8')))(Div(Style(Junctborder:2pxred(Junctmargin-top:50pxwidth:100%)))(Div(Style(Junctwidth:24%(Junctheight:24px(Junctmargin-left:automargin-right:auto))))(P'12')))))))",
  "(Div(Style(Junctborder:2%greenwidth:100%))(Compose(Div(Style(Junctborder:3pxbluewidth:5%))(P'12'))(Compose(Div(Stylemargin-left:36px)(P'F'))(Compose(Compose(Div(Style(Junctborder:2pxblue(Junctwidth:50%(Junctmargin-left:8pxmargin-right:auto))))(Compose(P'100')(Compose(P'100')(Compose(P'100')(Compose(P'100')(P'100'))))))(Div(Style(Junctwidth:24%(Junctmargin-right:8pxmargin-left:auto)))(P'8')))(Div(Style(Junctborder:2pxred(Junctmargin-top:50pxwidth:100%)))(Div(Style(Junctwidth:24%(Junctheight:24px(Junctmargin-left:automargin-right:auto))))(P'12')))))))",
  "(Div(Style(Junctborder:2%greenwidth:100%))(Compose(Div(Style(Junctborder:3pxbluewidth:5%))(P'12'))(Compose(Div(Stylemargin-left:36px)(P'F'))(Compose(Compose(Div(Style(Junctborder:2pxblue(Junctwidth:50%(Junctmargin-left:automargin-right:auto))))(Compose(P'100')(Compose(P'100')(Compose(P'100')(Compose(P'100')(P'100'))))))(Div(Style(Junctwidth:24%(Junctmargin-right:8pxmargin-left:auto)))(P'8')))(Div(Style(Junctborder:2pxred(Junctmargin-top:50pxwidth:100%)))(Div(Style(Junctwidth:24%(Junctheight:24px(Junctmargin-left:automargin-right:auto))))(P'12')))))))",
  "(Div(Style(Junctborder:2%greenwidth:100%))(Compose(Div(Style(Junctborder:3pxbluewidth:100%))(P'12'))(Compose(Div(Stylemargin-left:36px)(P'F'))(Compose(Compose(Div(Style(Junctborder:2pxblue(Junctwidth:50%(Junctmargin-left:automargin-right:auto))))(Compose(P'100')(Compose(P'100')(Compose(P'100')(Compose(P'100')(P'100'))))))(Div(Style(Junctwidth:24%(Junctmargin-right:8pxmargin-left:auto)))(P'8')))(Div(Style(Junctborder:2pxred(Junctmargin-top:50pxwidth:100%)))(Div(Style(Junctwidth:24%(Junctheight:24px(Junctmargin-left:automargin-right:auto))))(P'12')))))))",
  "(Div(Style(Junctborder:2pxgreenwidth:100%))(Compose(Div(Style(Junctborder:3pxbluewidth:100%))(P'12'))(Compose(Div(Stylemargin-left:36px)(P'F'))(Compose(Compose(Div(Style(Junctborder:2pxblue(Junctwidth:50%(Junctmargin-left:automargin-right:auto))))(Compose(P'100')(P'100')))(Div(Style(Junctwidth:24%(Junctmargin-right:8pxmargin-left:auto)))(P'8')))(Div(Style(Junctborder:2pxred(Junctmargin-top:50pxwidth:100%)))(Div(Style(Junctwidth:24%(Junctheight:24px(Junctmargin-left:automargin-right:auto))))(P'12')))))))",
  "(Div(Style(Junctborder:2pxgreenwidth:100%))(Compose(Div(Style(Junctborder:3pxbluewidth:100%))(P'12'))(Compose(Div(Stylemargin-left:36px)(P'F'))(Compose(Compose(Div(Style(Junctborder:2pxblue(Junctwidth:50%(Junctmargin-left:automargin-right:auto))))(Compose(P'100')(Compose(P'100')(P'100'))))(Div(Style(Junctwidth:24%(Junctmargin-right:8pxmargin-left:auto)))(P'8')))(Div(Style(Junctborder:2pxred(Junctmargin-top:50pxwidth:100%)))(Div(Style(Junctwidth:24%(Junctheight:24px(Junctmargin-left:automargin-right:auto))))(P'12')))))))",
];
const html_expressions = [
  "<html><body><div style='border: 2px solid green; width: 100px'><div style='width: 24px; margin-top: auto; margin-left: 11%; width: 24px; border: 8px solid red; margin-left: 3px; width: 2px; width: 50%; width: 2px; margin-left: 2px; margin-right: 24%; border: 100% solid red; margin-left: auto'><p>Lorem IpsumL</p></div><div style='margin-left: 36px'><p>Lorem IpsumLore</p></div><div style='border: 2px solid blue; border: 50% solid green; margin-left: auto; margin-right: auto'><p>Lorem IpsumLorem IpsumLorem IpsumLorem IpsumLorem IpsumLorem IpsumLorem IpsumLorem IpsumLorem IpsumL</p><p>Lorem IpsumLorem IpsumLorem IpsumLorem IpsumLorem IpsumLorem IpsumLorem IpsumLorem IpsumLorem IpsumL</p><p>Lorem IpsumLorem IpsumLorem IpsumLorem IpsumLorem IpsumLorem IpsumLorem IpsumLorem IpsumLorem IpsumL</p></div><div style='width: 24%; margin-right: 8px; margin-left: 7px'><p>Lorem Ip</p></div><div style='border: 2px solid red; margin-top: 50px; width: 100%'><div style='width: 24%; height: 24px; margin-left: auto; margin-right: auto'><p>Lorem IpsumL</p></div></div></div></body></html>",
  "<html><body><div style='border: 2px solid green; width: 100%'><div style='width: 24px; margin-top: auto; margin-left: 11%; width: 24px; border: 8px solid red; margin-left: 3px; width: 2px; width: 50%; width: 2px; margin-left: 2px; margin-right: 24%; border: 50% solid red; margin-left: auto'><p>Lorem IpsumL</p></div><div style='margin-left: 36px'><p>Lorem IpsumLore</p></div><p>Lorem IpsumLorem IpsumLorem IpsumLorem IpsumLorem IpsumLorem IpsumLorem IpsumLorem IpsumLorem IpsumL</p><div style='width: 24%; margin-right: 8px; margin-left: 7px'><p>Lorem Ip</p></div><div style='border: 2% solid red; margin-top: 50px; width: 100%'><div style='width: 24%; height: 24px; margin-left: auto; margin-right: auto'><p>Lorem IpsumL</p></div></div></div></body></html>",
  "<html><body><div style='border: 2px solid green; width: 100%'><div style='width: 24px; margin-top: auto; margin-left: 11%; width: 24px; border: 8px solid red; margin-left: 3px; width: 2px; width: 50%; width: 2px; margin-left: 2px; margin-right: 24%; border: 50% solid red; margin-left: auto'><p>Lorem IpsumL</p></div><div style='margin-left: 36px'><p>Lorem IpsumLore</p></div><p>Lorem IpsumLorem IpsumLorem IpsumLorem IpsumLorem IpsumLorem IpsumLorem IpsumLorem IpsumLorem IpsumL</p><div style='width: 24%; margin-right: 8px; margin-left: 7px'><p>Lorem Ip</p></div><div style='border: 2px solid red; margin-top: 50px; width: 100%'><div style='width: 24%; height: 24px; margin-left: auto; margin-right: auto'><p>Lorem IpsumL</p></div></div></div></body></html>",
  "<html><body><div style='border: 24% solid blue; width: 2px'><div style='border: 3px solid blue; width: 5%'><p>Lorem IpsumLorem IpsumLorem IpsumLor</p></div><div style='width: 24%'><p>Lorem IpsumLore</p></div><div style='margin-top: 50px; width: 50%; margin-left: 8px; margin-right: auto'><p>Lorem IpsumLorem IpsumLorem IpsumLorem IpsumLorem IpsumLorem IpsumLorem IpsumLorem IpsumLorem IpsumL</p><p>Lorem IpsumLorem IpsumLorem IpsumLorem IpsumLorem IpsumLorem IpsumLorem IpsumLorem IpsumLorem IpsumL</p><p>Lorem IpsumLorem IpsumLorem IpsumLorem IpsumLorem IpsumLorem IpsumLorem IpsumLorem IpsumLorem IpsumL</p></div><div style='width: 24%; margin-right: 8px; margin-left: auto'><p>Lorem Ip</p></div><div style='border: 2px solid red; margin-top: 50px; margin-right: 100%'><div style='width: 24%; height: 24px; margin-left: 10%; margin-right: auto'><p>Lorem IpsumL</p></div></div></div></body></html>",
  "<html><body><div style='border: 24% solid blue; width: 2px'><div style='border: 3px solid blue; width: 5%'><p>Lorem IpsumLorem IpsumLorem IpsumLor</p></div><div style='width: 24%'><p>Lorem IpsumLore</p></div><div style='margin-top: 50px; margin-right: auto; height: 8px'><p>Lorem IpsumLorem IpsumLorem IpsumLorem IpsumLorem IpsumLorem IpsumLorem IpsumLorem IpsumLorem IpsumL</p><p>Lorem IpsumLorem IpsumLorem IpsumLorem IpsumLorem IpsumLorem IpsumLorem IpsumLorem IpsumLorem IpsumL</p><p>Lorem IpsumLorem IpsumLorem IpsumLorem IpsumLorem IpsumLorem IpsumLorem IpsumLorem IpsumLorem IpsumL</p></div><div style='width: 24%; margin-right: 8px; margin-left: auto'><p>Lorem Ip</p></div><div style='border: 2px solid red; margin-top: 50px; margin-right: 100%'><div style='width: 24%; height: 24px; margin-left: 10%; margin-right: auto'><p>Lorem IpsumL</p></div></div></div></body></html>",
  "<html><body><div style='border: 24% solid blue; width: 2px'><div style='border: 3px solid blue; width: 5%'><p>Lorem IpsumLorem IpsumLorem IpsumLor</p></div><div style='width: 24%'><p>Lorem IpsumLore</p></div><div style='margin-top: 50px; width: 50%; margin-left: 8px; margin-right: auto'><p>Lorem IpsumLorem IpsumLorem IpsumLorem IpsumLorem IpsumLorem IpsumLorem IpsumLorem IpsumLorem IpsumL</p><p>Lorem IpsumLorem IpsumLorem IpsumLorem IpsumLorem IpsumLorem IpsumLorem IpsumLorem IpsumLorem IpsumL</p><p>Lorem IpsumL</p><p>Lorem IpsumLorem IpsumLorem IpsumLorem IpsumLorem IpsumLorem IpsumLorem IpsumLorem IpsumLorem IpsumL</p><p>Lorem IpsumLorem IpsumLorem IpsumLorem IpsumLorem IpsumLorem IpsumLorem IpsumLorem IpsumLorem IpsumL</p></div><div style='width: 24%; margin-right: 8px; margin-left: auto'><p>Lorem Ip</p></div><div style='border: 2px solid red; margin-top: 50px; margin-right: 100%'><div style='width: 24%; height: 24px; margin-left: 10%; margin-right: auto'><p>Lorem IpsumL</p></div></div></div></body></html>",
  "<html><body><div style='border: 24px solid blue; width: 2px'><div style='border: 3px solid blue; width: 5%'><p>Lorem IpsumLorem IpsumLorem IpsumLor</p></div><div style='width: 24%'><p>Lorem IpsumLore</p></div><div style='margin-right: 100%; width: 50%; margin-left: 8px; margin-right: auto'><p>Lorem IpsumLorem IpsumLorem IpsumLorem IpsumLorem IpsumLorem IpsumLorem IpsumLorem IpsumLorem IpsumL</p><p>Lorem IpsumLorem IpsumLorem IpsumLorem IpsumLorem IpsumLorem IpsumLorem IpsumLorem IpsumLorem IpsumL</p><p>Lorem IpsumL</p><p>Lorem IpsumLorem IpsumLorem IpsumLorem IpsumLorem IpsumLorem IpsumLorem IpsumLorem IpsumLorem IpsumL</p><p>Lorem IpsumLorem IpsumLorem IpsumLorem IpsumLorem IpsumLorem IpsumLorem IpsumLorem IpsumLorem IpsumL</p></div><div style='width: 24%; margin-right: 8px; margin-left: auto'><p>Lorem Ip</p></div><div style='border: 2px solid red; margin-top: 50px; margin-right: 100%'><div style='width: 24%; height: 24px; margin-left: 10%; margin-right: auto'><p>Lorem IpsumL</p></div></div></div></body></html>",
  "<html><body><div style='border: 24px solid blue; width: 2px'><div style='border: 3px solid blue; width: 5%'><p>Lorem IpsumLorem IpsumLorem IpsumLor</p></div><div style='width: 24%'><p>Lorem IpsumLore</p></div><div style='border: 2px solid blue; width: 50%; margin-left: 8px; margin-right: auto'><p>Lorem IpsumLorem IpsumLorem IpsumLorem IpsumLorem IpsumLorem IpsumLorem IpsumLorem IpsumLorem IpsumL</p><p>Lorem IpsumLorem IpsumLorem IpsumLorem IpsumLorem IpsumLorem IpsumLorem IpsumLorem IpsumLorem IpsumL</p><p>Lorem IpsumL</p><p>Lorem IpsumLorem IpsumLorem IpsumLorem IpsumLorem IpsumLorem IpsumLorem IpsumLorem IpsumLorem IpsumL</p><p>Lorem IpsumLorem IpsumLorem IpsumLorem IpsumLorem IpsumLorem IpsumLorem IpsumLorem IpsumLorem IpsumL</p></div><div style='width: 24%; margin-right: 8px; margin-left: auto'><p>Lorem Ip</p></div><div style='border: 2px solid red; margin-top: 50px; margin-right: 100%'><div style='width: 24%; height: 24px; margin-left: 10%; margin-right: auto'><p>Lorem IpsumL</p></div></div></div></body></html>",
  "<html><body><div style='border: 2% solid green; width: 2px'><div style='border: 3px solid blue; width: 5%'><p>Lorem IpsumL</p></div><div style='height: 50%'><p>Lorem IpsumLore</p></div><div style='border: 2px solid blue; width: 50%; margin-left: 8px; margin-right: auto'><p>Lorem IpsumLorem IpsumLorem IpsumLorem IpsumLorem IpsumLorem IpsumLorem IpsumLorem IpsumLorem IpsumL</p><p>Lorem IpsumLorem IpsumLorem IpsumLorem IpsumLorem IpsumLorem IpsumLorem IpsumLorem IpsumLorem IpsumL</p><p>Lorem IpsumLorem IpsumLorem IpsumLorem IpsumLorem IpsumLorem IpsumLorem IpsumLorem IpsumLorem IpsumL</p><p>Lorem IpsumLorem IpsumLorem IpsumLorem IpsumLorem IpsumLorem IpsumLorem IpsumLorem IpsumLorem IpsumL</p><p>Lorem IpsumLorem IpsumLorem IpsumLorem IpsumLorem IpsumLorem IpsumLorem IpsumLorem IpsumLorem IpsumL</p></div><div style='width: 24%; margin-right: 8px; margin-left: auto'><p>Lorem Ip</p></div><div style='border: 2px solid red; margin-top: 50px; width: 100%'><div style='width: 24%; height: 24px; margin-left: auto; margin-right: auto'><p>Lorem IpsumL</p></div></div></div></body></html>",
  "<html><body><div style='border: 2% solid green; width: 2px'><div style='border: 3px solid blue; width: 5%'><p>Lorem IpsumL</p></div><div style='margin-left: 36px'><p>Lorem IpsumLore</p></div><div style='border: 2px solid blue; width: 50%; margin-left: 8px; margin-right: auto'><p>Lorem IpsumLorem IpsumLorem IpsumLorem IpsumLorem IpsumLorem IpsumLorem IpsumLorem IpsumLorem IpsumL</p><p>Lorem IpsumLorem IpsumLorem IpsumLorem IpsumLorem IpsumLorem IpsumLorem IpsumLorem IpsumLorem IpsumL</p><p>Lorem IpsumLorem IpsumLorem IpsumLorem IpsumLorem IpsumLorem IpsumLorem IpsumLorem IpsumLorem IpsumL</p><p>Lorem IpsumLorem IpsumLorem IpsumLorem IpsumLorem IpsumLorem IpsumLorem IpsumLorem IpsumLorem IpsumL</p><p>Lorem IpsumLorem IpsumLorem IpsumLorem IpsumLorem IpsumLorem IpsumLorem IpsumLorem IpsumLorem IpsumL</p></div><div style='width: 24%; margin-right: 8px; margin-left: auto'><p>Lorem Ip</p></div><div style='border: 2px solid red; margin-top: 50px; width: 100%'><div style='width: 24%; height: 24px; margin-left: auto; margin-right: auto'><p>Lorem IpsumL</p></div></div></div></body></html>",
  "<html><body><div style='border: 2% solid green; width: 100%'><div style='border: 3px solid blue; width: 5%'><p>Lorem IpsumL</p></div><div style='margin-left: 36px'><p>Lorem IpsumLore</p></div><div style='border: 2px solid blue; width: 50%; margin-left: 8px; margin-right: auto'><p>Lorem IpsumLorem IpsumLorem IpsumLorem IpsumLorem IpsumLorem IpsumLorem IpsumLorem IpsumLorem IpsumL</p><p>Lorem IpsumLorem IpsumLorem IpsumLorem IpsumLorem IpsumLorem IpsumLorem IpsumLorem IpsumLorem IpsumL</p><p>Lorem IpsumLorem IpsumLorem IpsumLorem IpsumLorem IpsumLorem IpsumLorem IpsumLorem IpsumLorem IpsumL</p><p>Lorem IpsumLorem IpsumLorem IpsumLorem IpsumLorem IpsumLorem IpsumLorem IpsumLorem IpsumLorem IpsumL</p><p>Lorem IpsumLorem IpsumLorem IpsumLorem IpsumLorem IpsumLorem IpsumLorem IpsumLorem IpsumLorem IpsumL</p></div><div style='width: 24%; margin-right: 8px; margin-left: auto'><p>Lorem Ip</p></div><div style='border: 2px solid red; margin-top: 50px; width: 100%'><div style='width: 24%; height: 24px; margin-left: auto; margin-right: auto'><p>Lorem IpsumL</p></div></div></div></body></html>",
  "<html><body><div style='border: 2% solid green; width: 100%'><div style='border: 3px solid blue; width: 5%'><p>Lorem IpsumL</p></div><div style='margin-left: 36px'><p>Lorem IpsumLore</p></div><div style='border: 2px solid blue; width: 50%; margin-left: auto; margin-right: auto'><p>Lorem IpsumLorem IpsumLorem IpsumLorem IpsumLorem IpsumLorem IpsumLorem IpsumLorem IpsumLorem IpsumL</p><p>Lorem IpsumLorem IpsumLorem IpsumLorem IpsumLorem IpsumLorem IpsumLorem IpsumLorem IpsumLorem IpsumL</p><p>Lorem IpsumLorem IpsumLorem IpsumLorem IpsumLorem IpsumLorem IpsumLorem IpsumLorem IpsumLorem IpsumL</p><p>Lorem IpsumLorem IpsumLorem IpsumLorem IpsumLorem IpsumLorem IpsumLorem IpsumLorem IpsumLorem IpsumL</p><p>Lorem IpsumLorem IpsumLorem IpsumLorem IpsumLorem IpsumLorem IpsumLorem IpsumLorem IpsumLorem IpsumL</p></div><div style='width: 24%; margin-right: 8px; margin-left: auto'><p>Lorem Ip</p></div><div style='border: 2px solid red; margin-top: 50px; width: 100%'><div style='width: 24%; height: 24px; margin-left: auto; margin-right: auto'><p>Lorem IpsumL</p></div></div></div></body></html>",
  "<html><body><div style='border: 2% solid green; width: 100%'><div style='border: 3px solid blue; width: 100%'><p>Lorem IpsumL</p></div><div style='margin-left: 36px'><p>Lorem IpsumLore</p></div><div style='border: 2px solid blue; width: 50%; margin-left: auto; margin-right: auto'><p>Lorem IpsumLorem IpsumLorem IpsumLorem IpsumLorem IpsumLorem IpsumLorem IpsumLorem IpsumLorem IpsumL</p><p>Lorem IpsumLorem IpsumLorem IpsumLorem IpsumLorem IpsumLorem IpsumLorem IpsumLorem IpsumLorem IpsumL</p><p>Lorem IpsumLorem IpsumLorem IpsumLorem IpsumLorem IpsumLorem IpsumLorem IpsumLorem IpsumLorem IpsumL</p><p>Lorem IpsumLorem IpsumLorem IpsumLorem IpsumLorem IpsumLorem IpsumLorem IpsumLorem IpsumLorem IpsumL</p><p>Lorem IpsumLorem IpsumLorem IpsumLorem IpsumLorem IpsumLorem IpsumLorem IpsumLorem IpsumLorem IpsumL</p></div><div style='width: 24%; margin-right: 8px; margin-left: auto'><p>Lorem Ip</p></div><div style='border: 2px solid red; margin-top: 50px; width: 100%'><div style='width: 24%; height: 24px; margin-left: auto; margin-right: auto'><p>Lorem IpsumL</p></div></div></div></body></html>",
  "<html><body><div style='border: 2px solid green; width: 100%'><div style='border: 3px solid blue; width: 100%'><p>Lorem IpsumL</p></div><div style='margin-left: 36px'><p>Lorem IpsumLore</p></div><div style='border: 2px solid blue; width: 50%; margin-left: auto; margin-right: auto'><p>Lorem IpsumLorem IpsumLorem IpsumLorem IpsumLorem IpsumLorem IpsumLorem IpsumLorem IpsumLorem IpsumL</p><p>Lorem IpsumLorem IpsumLorem IpsumLorem IpsumLorem IpsumLorem IpsumLorem IpsumLorem IpsumLorem IpsumL</p></div><div style='width: 24%; margin-right: 8px; margin-left: auto'><p>Lorem Ip</p></div><div style='border: 2px solid red; margin-top: 50px; width: 100%'><div style='width: 24%; height: 24px; margin-left: auto; margin-right: auto'><p>Lorem IpsumL</p></div></div></div></body></html>",
  "<html><body><div style='border: 2px solid green; width: 100%'><div style='border: 3px solid blue; width: 100%'><p>Lorem IpsumL</p></div><div style='margin-left: 36px'><p>Lorem IpsumLore</p></div><div style='border: 2px solid blue; width: 50%; margin-left: auto; margin-right: auto'><p>Lorem IpsumLorem IpsumLorem IpsumLorem IpsumLorem IpsumLorem IpsumLorem IpsumLorem IpsumLorem IpsumL</p><p>Lorem IpsumLorem IpsumLorem IpsumLorem IpsumLorem IpsumLorem IpsumLorem IpsumLorem IpsumLorem IpsumL</p><p>Lorem IpsumLorem IpsumLorem IpsumLorem IpsumLorem IpsumLorem IpsumLorem IpsumLorem IpsumLorem IpsumL</p></div><div style='width: 24%; margin-right: 8px; margin-left: auto'><p>Lorem Ip</p></div><div style='border: 2px solid red; margin-top: 50px; width: 100%'><div style='width: 24%; height: 24px; margin-left: auto; margin-right: auto'><p>Lorem IpsumL</p></div></div></div></body></html>",
];

export function Home({ targetImage }: Props) {
  const imageUrl = URL.createObjectURL(targetImage);
  const [currentIndex, setCurrentIndex] = useState(0);
  const intervalTime = 1500;
  const initialDelay = 2000;

  useEffect(() => {
    const intervalId = setInterval(() => {
      setCurrentIndex((prevIndex) =>
        Math.min(prevIndex + 1, expressions.length - 1)
      );
    }, intervalTime);
    return () => clearInterval(intervalId);
  }, []);

  useEffect(() => {
    console.log("Current Index: ", currentIndex);
  }, [currentIndex]);

  return (
    <div
      style={{
        display: "flex",
        width: "100%",
        height: "100vh",
        overflow: "hidden",
      }}
    >
      <div
        style={{
          width: "50%",
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          justifyContent: "center",
          padding: "10px",
        }}
      >
        <div
          style={{ marginBottom: "10px", textAlign: "center", width: "100%" }}
        >
          <div style={{ fontSize: "20px", marginBottom: "10px" }}>
            Target Image
          </div>
          <img
            src={imageUrl}
            alt="Uploaded Target"
            style={{
              maxWidth: "100%",
              maxHeight: "30vh",
              borderRadius: "8px",
            }}
          />
        </div>
        <div
          style={{
            width: "100%",
            padding: "10px",
            fontFamily: "'Courier New', monospace",
            fontSize: "16px",
            whiteSpace: "pre-wrap",
            backgroundColor: "#f4f4f4",
            borderRadius: "8px",
            marginBottom: "10px",
            border: "1px solid #ddd",
          }}
        >
          <div style={{ fontSize: "16px", marginBottom: "10px" }}>
            Expression
          </div>
          {expressions[currentIndex]}
        </div>
        <div
          style={{
            width: "100%",
            padding: "10px",
            fontFamily: "'Courier New', monospace",
            fontSize: "16px",
            whiteSpace: "pre-wrap",
            backgroundColor: "#fff",
            borderRadius: "8px",
          }}
        >
          <div style={{ fontSize: "16px", marginBottom: "10px" }}>
            Raw HTML Expression
          </div>
          {html_expressions[currentIndex]}
        </div>
      </div>
      <div
        style={{
          width: "50%",
          height: "90vh",
          padding: "10px",
          borderRadius: "8px",
        }}
      >
        <div style={{ fontSize: "16px" }}>Rendered HTML</div>
        <div
          dangerouslySetInnerHTML={{ __html: html_expressions[currentIndex] }}
        ></div>
      </div>
    </div>
  );
}