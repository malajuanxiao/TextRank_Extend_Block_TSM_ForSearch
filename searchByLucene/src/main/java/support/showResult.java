package support;

import entity.Que;

import java.util.ArrayList;
import java.util.List;

public class showResult {
    private double meanPresion;
    private double meanRecall;
    private double FValue;
    public List<Double> Plist = new ArrayList<Double>();
    public List<Double> Rlist = new ArrayList<Double>();
    public List<Double> Flist = new ArrayList<Double>();
    private double mAP;

    public void getPR(List<Que> queryList , int top, int n ){
        Plist.clear();
        Rlist.clear();
        int quSum = queryList.size();

        int answerSum = 0;
        int answerGet;

        for(Que query:queryList){
            answerGet = 0;
            double nowP = 0; double nowR = 0; double Fn = 0;

            answerSum = query.getReply().size();
            for (int i = 0; i<top; i++){
                String rdoc_no = query.getResultList().get(i).getDoc_no();
                if(query.getReply().contains(rdoc_no)){
                    answerGet++;
                }
            }
            nowP = answerGet * 1.0 /top;
            nowR = answerGet * 1.0 /answerSum;
            if (nowP + nowR != 0 ){
                Fn = 2 * nowP * nowR / (nowP + nowR);
            }
            meanPresion += nowP;
            meanRecall += nowR;
            FValue += Fn;
            //System.out.println(query.getId()+ ": P(" + nowP + "),R(" + nowR + "),F1(" + Fn +")");
            Plist.add(nowP);
            Rlist.add(nowR);
            Flist.add(Fn);
        }
        meanPresion /= quSum;
        meanRecall /= quSum;
        FValue /= quSum;
    }

    public double getMAP(List<Que> queryList , int maxlength, int evaCount ){
        List<Double> aRList = initList(maxlength);
        List<Double> aPList = initList(maxlength);
        List<Double> xRecall = new ArrayList<>();
        List<Double> yPresion = new ArrayList<>();
        int quSum = queryList.size();
        double nowP = 0;
        double nowR = 0;
        int answerSum = 0;
        int answerGet;
        int currentlength;


        for(Que query: queryList){

            currentlength = query.getResultList().size();
            if(currentlength>=maxlength){
                currentlength = maxlength;
            }
            answerGet = 0;
            answerSum = query.getReply().size();
            for(int i =0; i<currentlength; i++){
                String rdoc_no = query.getResultList().get(i).getDoc_no();
                if(query.getReply().contains(rdoc_no)){
                    answerGet++;
                }
                nowP = answerGet * 1.0 /i;
                nowR = answerGet * 1.0 /answerSum;
                aPList.set(i, aPList.get(i)+nowP);
                aRList.set(i, aRList.get(i)+nowR);
                aRList.add(nowR);
            }
            for(int i = currentlength; i<maxlength; i++){
                nowP = answerGet * 1.0 /i;
                aPList.set(i, aPList.get(i)+nowP);
                aRList.set(i, aRList.get(i)+nowR);
            }
            //System.out.print("|");
        }

        double step = 1.0/evaCount;
        xRecall.add(0.0);
        yPresion.add(aPList.get(0));
        mAP = 0.0;
        double currentX = step;

        for(int i = 0; i<maxlength; i++){
            nowR = aRList.get(i)/quSum;
            if(nowR >= currentX){
                currentX += step;
                nowP = aPList.get(i)/quSum;
                xRecall.add(nowR);
                yPresion.add(nowP);
                mAP += nowP;
            }
        }
        /*
        System.out.println(evaCount);
        System.out.println(xRecall);
        System.out.println(yPresion);
         */
        mAP /= yPresion.size();
        return mAP;
    }

    public List<Double> initList(int length){
        List<Double> iniList= new ArrayList<>();
        for(int i = 0; i<length; i++){
            iniList.add(0.0);
        }
        return iniList;
    }



    public double getMeanPresion() {
        return meanPresion;
    }

    public double getMeanRecall() {
        return meanRecall;
    }

    public double getFValue() {
        return FValue;
    }

    public double getmAP() {
        return mAP;
    }

}
