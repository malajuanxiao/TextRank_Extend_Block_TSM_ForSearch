package entity;

public class Result {
    private float score;
    private String doc_no;

    public Result(float score, String doc_no) {
        this.score = score;
        this.doc_no = doc_no;
    }

    public float getScore() {
        return score;
    }

    public void setScore(float score) {
        this.score = score;
    }

    public String getDoc_no() {
        return doc_no;
    }

    public void setDoc_no(String doc_no) {
        this.doc_no = doc_no;
    }

    @Override
    public String toString() {
        return "Result{" +
                "score=" + score +
                ", doc_no='" + doc_no + '\'' +
                '}';
    }
}
