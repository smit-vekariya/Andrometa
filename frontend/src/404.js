const Page404 = () => {
    const styles = {
        root: {
          fontFamily: 'Arial, sans-serif',
          margin: 0,
          padding: 0,
          display: 'flex',
          justifyContent: 'center',
          alignItems: 'center',
          height: '80vh',
          flexDirection: 'column',
        },
        container: {
          textAlign: 'center',
          padding: '20px',
        },
        title: {
          fontSize: '2em',
          color: '#333',
          marginBottom: '10px',
        },
        text: {
          fontSize: '1.2em',
          color: '#666',
        },
      };
    return (
        <>
            <div style={styles.root}>
                <div style={styles.container}>
                    <h1 style={styles.title}>404 - Page Not Found</h1>
                    <p style={styles.text}>
                    The page you are looking for might have been removed, had its name changed, or is temporarily unavailable.
                    </p>
                </div>
            </div>
        </>
    );
}

export default Page404;