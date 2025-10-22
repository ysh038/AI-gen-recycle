import styles from './Home.module.css'
import { useAuthStore } from '../../stores/shared/user'

function Home() {
    const user = useAuthStore((state) => state.user)
    return (
        <main className={styles.main}>
            <h1>테스트 로그인 성공</h1>
            <p>사용자 정보: {user?.user_id}</p>
            <p>이메일: {user?.email}</p>
        </main>
    )
}

export default Home
