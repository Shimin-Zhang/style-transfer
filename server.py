from flask import Flask
from flask import render_template
from flask import request

from model.code.main.load_model_demo import PreProcessing as prepro
from model.code.main.load_model_demo import Demo

app = Flask(__name__)

demo = Demo()
demo.loadModel("data/pointer_model7.ckpt")

def padUp(line,finalLength,paddingMethod):
    words=line.split()
    words=["<s>",]+words+["</s>",]
    lineLength=len(words)
    padLength=finalLength-lineLength
    if padLength>0:
        if paddingMethod=="pre":
            words=["<p>"]*padLength+words
        elif paddingMethod=="post":
            words=words+["<p>",]*padLength
    elif padLength<0:
        words=words[:finalLength]

    return words

def copy_mechanism(input, output, alpha):
    inputLines = [padUp(line, 25, "pre") for line in input]
    hypLines = [padUp(line, 24, "post") for line in output]
    outputLines = []

    for i in range(len(inputLines)):
        hypLine=hypLines[i]
        inpLine=inputLines[i]
        attentionMatrix=alpha[i]

        inputStartIndex=-1
        for x in inpLine:
            if x != "<p>":
                break
            else:
                inputStartIndex += 1

        hypEndIndex = 0

        for x in hypLine:
            if x == "<p>":
                break
            else:
                hypEndIndex += 1

        hypLine=hypLine[:hypEndIndex]
        inpLine=inpLine[inputStartIndex+1:]

        attentionMatrix = attentionMatrix[:hypEndIndex,inputStartIndex+1:]
        newHypLine = []

        for k, x in enumerate(hypLine):

            if x == "<s>" or x == "</s>":
                continue
            elif x != "unk":
                newHypLine.append(x)
            else:
                attentionList=list(attentionMatrix[k])
                maxAttention=max(attentionList)
                maxAttentionIndices=[j for j,a in enumerate(attentionList) if a==maxAttention]
                maxAttentionIndex=maxAttentionIndices[0]
                xNew=inpLine[maxAttentionIndex]
                newHypLine.append(xNew)

        outputLines.append((" ").join(newHypLine))
    return outputLines


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/inference', methods=['POST'])
def inference():
    if request.method == 'POST':
        text_input = request.form['text']
        text_input = text_input.split("\n")
        print 'new text input:', text_input
        text_output, alpha = demo.getOutput(text_input)
        outputs = copy_mechanism(text_input, text_output, alpha)
        return ('').join(outputs)




