package support;

import entity.Que;
import parse.QUHandler;

import javax.xml.parsers.SAXParser;
import javax.xml.parsers.SAXParserFactory;
import java.io.*;
import java.util.*;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

public class fetchTestData {




    public static List<Que> fetchReply(List<Que> queryList) throws IOException {
        HashMap<String,Set<String>> reply = new HashMap<>();
        File readfile = new File("E:\\Indexfile\\disk\\qrels.txt");
        BufferedReader in = new BufferedReader(new FileReader(readfile));
        String str = in.readLine();
        String[] relInfo;
        while(str!=null) {
            relInfo = str.split(" ");
            if(!relInfo[3].trim().equals("0")){
                if(reply.containsKey(relInfo[0])){
                    reply.get(relInfo[0]).add(relInfo[2]);
                }else {
                    Set<String> s = new TreeSet<>();
                    s.add(relInfo[2]);
                    reply.put(relInfo[0],s);
                }

            }
            str = in.readLine();
        }
        //System.out.println(reply);
        for(Que query : queryList){
            query.setReply(reply.get(Integer.toString(query.getId())));
        }

        return queryList;
    }






    public static List<Que> fetchQuery() {
        List<Que> queryList = new ArrayList<>();
        File readfile = new File("E:\\Indexfile\\disk\\quset");
        File loadfile = new File("E:\\Indexfile\\disk\\TREC\\test\\qusettest");
        Pattern r1 = Pattern.compile("<num>");
        Pattern r2 = Pattern.compile("<title>");
        Pattern r3 = Pattern.compile("<desc>");
        Pattern r4 = Pattern.compile("<narr>");
        Pattern r5 = Pattern.compile("&|\\?|!");
        Pattern r6 = Pattern.compile("and/or");



        try {
            BufferedReader in = new BufferedReader(new FileReader(readfile));
            PrintWriter out = new PrintWriter(new FileWriter(loadfile));

            String str = in.readLine();
            while(str!=null) {
                str = str.trim();

                Matcher m1 = r1.matcher(str);
                if (m1.find()){
                    str = m1.replaceAll("num:");
                }
                Matcher m2 = r2.matcher(str);
                if (m2.find()){
                    str = m2.replaceAll(" title:");
                }
                Matcher m3 = r3.matcher(str);
                if (m3.find()){
                    str = m3.replaceAll(" desc:");
                }
                Matcher m4 = r4.matcher(str);
                if (m4.find()){
                    str = m4.replaceAll(" narr:");
                }
                Matcher m5 = r5.matcher(str);
                if (m5.find()){
                    str = m5.replaceAll(" ");
                }
                Matcher m6 = r6.matcher(str);
                if (m6.find()){
                    str = m6.replaceAll("and or");
                }

                if (str != null && !str.equals("") && !str.equals("\n")) {
                    if(str.toCharArray()[0]=='<'){
                        out.println(str);
                    }else{
                        out.print(str.replace("\n"," "));
                    }
                }

                str = in.readLine();
            }
            in.close();
            out.close();
        }catch(FileNotFoundException e1) {
            System.err.println("File not found");
        }catch(IOException e2) {
            e2.printStackTrace();
        }

        try {
            SAXParserFactory spf = SAXParserFactory.newInstance();
            SAXParser parser = spf.newSAXParser();
            QUHandler handler = new QUHandler("top");
            FileInputStream input = new FileInputStream(loadfile);
            parser.parse(input, handler);
            input.close();
            queryList = handler.getQuerys();
            fetchReply(queryList);
        } catch (Exception e) {
            // TODO Auto-generated catch block
            e.printStackTrace();
        }

        return queryList;
    }

}
